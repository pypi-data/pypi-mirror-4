#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Sep 27 17:04:09 CEST 2012

import bob
import numpy

from . import *
from . import __doc__ as long_description

class ZNorm(Normalizer):
  """
  ZNorm normalization
  """

  def __init__(self):
    self.avg         = 0
    self.std         = 0

    self.totalScores = 0


  def set_scores(self,scores):
    self.avg =  numpy.average(scores,axis=0)
    self.std  = numpy.std(scores,axis=0)

    self.totalScores = len(scores)
  set_scores.__doc__ = Normalizer.set_scores.__doc__


  def __str__(self):
    string =  "ZNorm Normalization"
    
    return string


  def __call__(self,scores):
    return numpy.divide((scores - self.avg),self.std)
  __call__.__doc__ = Normalizer.__call__.__doc__
