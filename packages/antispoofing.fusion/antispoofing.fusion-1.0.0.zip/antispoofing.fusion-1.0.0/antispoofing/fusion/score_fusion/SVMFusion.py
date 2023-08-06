#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 20:50:00 CEST 2012

"""
This script run the score fusion

"""

import bob
import numpy

from . import *

class SVMFusion(ScoreFusion):

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

    #Trainning the SVM machine
    svm_trainer = bob.trainer.SVMTrainer()
    svm_trainer.probability = True
    #svm_trainer.kernel_type = bob.machine.svm_kernel_type.LINEAR
    self.__svm_machine = svm_trainer.train([positives, negatives])
  train.__doc__ = ScoreFusion.train.__doc__


  def __call__(self,scores):
	
    #Applying normalization
    if(self.normalizer!=None):
      scores = self.normalizer(scores)

    #Applying the SVM in the input data
    fused_scores = [self.__svm_machine.predict_class_and_scores(x)[1][0] for x in scores]
    #fused_scores = numpy.reshape(fused_scores,fused_scores.shape[0])

    return fused_scores
  __call__.__doc__ = ScoreFusion.__call__.__doc__


  def __str__(self):
    return "SVM Fusion"

