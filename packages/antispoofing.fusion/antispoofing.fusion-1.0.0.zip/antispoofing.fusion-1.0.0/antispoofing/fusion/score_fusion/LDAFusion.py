#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 20:50:00 CEST 2012

"""
This script run the score fusion

"""

import bob
import numpy

from . import *

from antispoofing.utils.ml import lda

class LDAFusion(ScoreFusion):

  """
  Implements the SVM Fusion
  """

  def __init__(self,normalizer=None):
    self.trainer_scores = None
    self.normalizer     = normalizer
	

  def train(self,trainer_scores=None):

    self.trainer_scores = trainer_scores

    if(len(trainer_scores)!=2):
      raise ValueError("It is necessary to have a tuple with len=2")

    positives = trainer_scores[0]
    negatives = trainer_scores[1]

    #Applying normalization
    if(self.normalizer!=None):
      positives = self.normalizer(positives)
      negatives = self.normalizer(negatives)

    train_data = [positives,negatives]
    self.__lda_machine = lda.make_lda(train_data)

  train.__doc__ = ScoreFusion.train.__doc__


  def __call__(self,scores):
	
    #Applying normalization
    if(self.normalizer!=None):
      scores = self.normalizer(scores)

    #Applying the SVM in the input data
    fused_scores = lda.get_scores(self.__lda_machine, scores)
    fused_scores = numpy.reshape(fused_scores,fused_scores.shape[0])

    return fused_scores
  __call__.__doc__ = ScoreFusion.__call__.__doc__

  def __str__(self):
    return "LDA Fusion"


