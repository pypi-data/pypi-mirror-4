#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import numpy
import bob

from ..score_fusion import *
import pkg_resources
import argparse


def main():

  #Fake data
  real_train_scores = numpy.random.rand(30,2)
  attack_train_scores = numpy.random.rand(30,2)
  data_to_normalization = numpy.concatenate((real_train_scores,attack_train_scores),axis=0)

  real_test_scores = numpy.random.rand(5,2)
  attack_test_scores = numpy.random.rand(5,2)


  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)


  #######
  # Database especific configuration
  #######
  ScoreFusion.create_parser(parser)
  args = parser.parse_args()
  fusion = ScoreFusion.load(args,data_to_normalization)
  fusion.train([real_train_scores,attack_train_scores])

  real_fused_scores = fusion(real_test_scores)
  attack_fused_scores = fusion(attack_test_scores)
  
  print("Scores after fusion")
  print(real_fused_scores)
  print(attack_fused_scores)
  print("######################### \n\n\n")


  #Simulating the Q-Statistic for 5 classifiers
  decisions = numpy.around(numpy.random.rand(100,8)).astype(int)
  print("Q-Average: " + str(ScoreFusion.QAverage(decisions)))
  
  
if __name__ == '__main__':
  main()
