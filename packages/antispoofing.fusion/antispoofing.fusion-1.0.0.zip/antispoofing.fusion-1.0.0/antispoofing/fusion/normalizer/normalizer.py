#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Sep 27 17:04:09 CEST 2012

import bob
import numpy

import abc

class Normalizer:
  """
  Class that implements some score normalization algorithms
  """

  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def set_scores(self,scores):
    """
    Constructor
    Setter with the scores

    scores 
        The base scores for normalization
    """

    

  @abc.abstractmethod
  def __call__(self,scores):
	"""
	Do the normalization
	
	Keyword Parameters:
	
    scores 
         The the scores to be normalized
	
	"""

