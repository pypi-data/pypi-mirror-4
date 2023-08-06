#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 20:50:00 CEST 2012

"""
This script run the score fusion

"""

import bob
import numpy

from .. import *

import abc

class ScoreFusion:
  """
Class that run different Score level fusion with different normalization score algorithm
"""

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def train(self,trainer_scores=None):
    """
Train the score fusion algorithm

trainer_scores
A set of scores to train the LLR

"""



  @abc.abstractmethod
  def __call__(self,scores):
    """
Get the fusion of scores using the LLR machine

Keyword Parameters:

scores
The Scores to be fused (numpy.array).

"""

  @staticmethod
  def computeStatistics(decisions):
    """
Compute the Q-Statistic between TWO classifiers following the algorithm proposed in:

Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy - LUDMILA I. KUNCHEVA AND CHRISTOPHER J. WHITAKER

QStatistic = (N11*N10 - N01*N10) / (N11*N10 + N01*N10)

Disagreement Measures = (N01*N10) / (N11 + N10 + N01 + N10)

double-fault measure = N00 / (N11 + N10 + N01 + N10)

Where -> N11 - When both classifiers agree
N00 - When both classifiers disagree
N10 - The first classifier make the correct decision and the second not
N01 - The first classifier make a mistake and the second not

How to interpret the QStatistic?
The output is float and the range of the output is -1 to 1.
QStatistic close to -1 means that both classifiers almost oppose each other and a fusion will be a disaster
QStatistic close to 0 means that both classifiers are statistically independent and a fusion will be good
QStatistic close to 1 means that both classifiers are almost the same and a fusion will not change anything


Results

Keyword Parameters:

decisions
numpy.array with the decisions of each classifier. 0 - wrong classification; 1 - correct classification

Example combining 2 classifiers: 0 0
1 1
0 0
1 0
"""
  
    if(len(decisions.shape)!=2):
      raise ValueError("Need a 2D numpy.array")

    #Only two classifiers
    if(decisions.shape[1] != 2):
      raise ValueError("Please, only two classifiers as input.")

    A = numpy.where(decisions[:,0] == 1)[0]
    B = numpy.where(decisions[:,1] == 1)[0]
    N11 = float(len(numpy.intersect1d(A,B)))

    A = numpy.where(decisions[:,0] == 0)[0]
    B = numpy.where(decisions[:,1] == 0)[0]
    N00 = float(len(numpy.intersect1d(A,B)))

    A = numpy.where(decisions[:,0] == 1)[0]
    B = numpy.where(decisions[:,1] == 0)[0]
    N10 = float(len(numpy.intersect1d(A,B)))

    A = numpy.where(decisions[:,0] == 0)[0]
    B = numpy.where(decisions[:,1] == 1)[0]
    N01 = float(len(numpy.intersect1d(A,B)))

    #Computing Q-Statistic
    qS = ((N11*N00) - (N01*N10)) / ((N11*N00) + (N01*N10))

    #Disagreement measure
    d = (N01 + N10) / (N11 + N00 + N01 + N10)

    #The double-fault measure
    df = N00 / (N11 + N00 + N01 + N10)

    return qS,d,df

  @staticmethod
  def QAverage(decisions):
    """
Compute the average between the QStatistics (Q-Average) following the algorithm proposed in:

Qav = 2/L(L-1) * sum(sum(QStatistic)), where L is the number

Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy - LUDMILA I. KUNCHEVA AND CHRISTOPHER J. WHITAKER

How to interpret the QAverage?
The output is float and the range of the output is -1 to 1.
QAverage close to -1 means that the classifiers almost oppose each other and a fusion will be a disaster
QAverage close to 0 means that the classifiers are statistically independent and a fusion will be good
QAverage close to 1 means that the classifiers are almost the same and a fusion will not change anything

Keyword Parameters:

decisions
numpy.array with the decisions of each classifier. 0 - wrong classification; 1 - correct classification

Example combining 3 classifiers: 0 0 0
1 1 1
0 0 1
1 1 0
"""

    if(len(decisions.shape)!=2):
      raise ValueError("Need a 2D numpy.array")

    if(decisions.shape[1] <= 1):
      raise ValueError("Need at least 2 classifiers.")

    L = decisions.shape[1]

    s = 0
    #Computing the SUM part
    for i in range(L-1):
      for j in range(i+1,L):
        qi = decisions[:,i].reshape(decisions.shape[0],1)
        qj = decisions[:,j].reshape(decisions.shape[0],1)

        qS,_,_ = ScoreFusion.computeStatistics(numpy.concatenate((qi,qj),axis=1))
        s = s + qS

    L = float(L)
    return (2/(L*(L-1))) * s


  ########
  # Static methods
  ########


  @staticmethod
  def create_parser(parser):
    """Defines a sub parser for each fusion algorithm, with optional properties.

Keyword Parameters:

parser
The argparse.ArgumentParser to which I'll attach the subparsers to

"""

    #For each resource (NORMALIZER.)
    import pkg_resources
    resource_name = 'antispoofing.fusion.normalizer'
    parser.add_argument('-n','--normalizer', type=str, default=None,
       choices=get_resources(resource_name), dest="normalizer",
       help='The Normalization algorithm (defaults to "%(default)s")')


    #For each resource (FUSION ALGS.)
    resource_name = 'antispoofing.fusion.score_fusion'
    parser.add_argument('-f','--fusion-algorithm', type=str, default='SUM',
        choices=get_resources(resource_name), dest="fusion_alg",
        help='The fusion algorithm (defaults to "%(default)s")')


  @staticmethod
  def load(args,normalization_scores=None):
    """
Load the Score Fusion algorithm with the specified normalization algorithm

Keyword Parameters:

args
The argparse.ArgumentParser

normalization_scores
The scores to generate the statistics for normalization
"""
    
    #loading normalizer
    normalizer = load_resources('antispoofing.fusion.normalizer',args.normalizer)
    if(normalizer != None):
      normalizer = normalizer()
      normalizer.set_scores(normalization_scores)

    #loading fusion
    fusion_alg = load_resources('antispoofing.fusion.score_fusion',args.fusion_alg)
    fusion_alg = fusion_alg()
    fusion_alg.normalizer = normalizer
    return fusion_alg
