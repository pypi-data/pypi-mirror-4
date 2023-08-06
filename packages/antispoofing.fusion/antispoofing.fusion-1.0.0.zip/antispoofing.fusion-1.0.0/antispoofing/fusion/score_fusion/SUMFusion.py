#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Oct 01 20:50:00 CEST 2012

import bob
import numpy

from . import *
from . import __doc__ as long_description

class SUMFusion(ScoreFusion):

  def __init__(self,normalizer=None):
    self.normalizer     = normalizer

  def train(self,trainer_scores=None):
    #Nothing to load
    return
  train.__doc__ = ScoreFusion.train.__doc__

  def __call__(self,scores):
    #Applying the score normalization    
    if(self.normalizer!=None):
      scores = self.normalizer(scores)


    #Applying the SUM rule in the input data
    fused_scores = numpy.sum(scores,axis=1)

    return fused_scores
  __call__.__doc__ = ScoreFusion.__call__.__doc__


  def __str__(self):
    return "SUM Fusion"


