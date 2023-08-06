#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Sep 27 17:04:09 CEST 2012

import bob
import numpy

from . import *
from . import __doc__ as long_description

class MinMaxNorm(Normalizer):
  """
  MinMax normalization
  """

  def __init__(self):
    self.mins = 0
    self.maxs = 0

    self.totalScores = 0

    self.lowerBound = -1
    self.upperBound = 1



  def set_scores(self,scores,lowerBound = -1, upperBound = 1):
    """
    Constructor
    
    Keyword Parameters:
    
    scores 
        The base scores for normalization

    lowerBound

    upperBound
    """
    
    self.mins = numpy.min(scores,axis=0)
    self.maxs = numpy.max(scores,axis=0)
    
    self.totalScores = len(scores)

    self.lowerBound = lowerBound
    self.upperBound = upperBound
  set_scores.__doc__ = Normalizer.set_scores.__doc__

  def __str__(self):
    string =  "MinMax Normalization"
    
    return string


  def __call__(self,scores):
    denom = self.maxs - self.mins
    normalizedScores = (self.upperBound - self.lowerBound) * (scores - self.mins) / denom + self.lowerBound

    return normalizedScores
  __call__.__doc__ = Normalizer.__call__.__doc__
