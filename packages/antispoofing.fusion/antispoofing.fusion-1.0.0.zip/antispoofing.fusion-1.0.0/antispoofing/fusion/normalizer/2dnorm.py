#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Sep 27 17:04:09 CEST 2012

import bob
import numpy

from . import *
from . import __doc__ as long_description

class twoDNorm(Normalizer):
  """
  ZNorm normalization
  """

  def __init__(self):
    self.std  = None
    self.avg  = None
    self.totalScores = None


  def set_scores(self,scores):
    self.avg =  numpy.average(scores,axis=0)
    self.std  = numpy.std(scores,axis=0)
    self.totalScores = len(scores)
  set_scores.__doc__ = Normalizer.set_scores.__doc__


  def __str__(self):
    string =  "2D Normalization"
    
    return string


  def __call__(self,scores):
    return numpy.divide(scores,2*self.std)
  __call__.__doc__ = Normalizer.__call__.__doc__
