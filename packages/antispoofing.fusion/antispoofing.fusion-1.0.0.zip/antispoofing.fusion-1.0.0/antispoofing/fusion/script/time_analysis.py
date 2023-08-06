#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import os, sys
import argparse
import numpy

import bob
from .. import ml
import antispoofing.utils.db 

def main():
     
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the scores of different countermeasures', nargs='+')
  
  parser.add_argument('-f', '--fusion-dir', type=str, dest='fusionDir', default='', help='Base directory containing the scores of different fusion strategies', nargs='+')    
  
  parser.add_argument('-e', '--end', action='store_true', default=False, help='Arg split')
    
  antispoofing.utils.db.Database.create_parser(parser, 'video')
  args = parser.parse_args()     
  db = args.cls(args) 
  # getting the parser variables
  scoresDir          = args.scoresDir
  fusionDir          = args.fusionDir 
  
  # perform time analysis for all videos using the given algorithms
  evolution_curves=[]    
  labels=[]
  for i in range(len(scoresDir)): 
    temp=ml.perf_fusion.time_analysis_per_video(scoresDir[i],db)
    evolution_curves.append(temp)
  
  for i in range(len(fusionDir)): 
    temp=ml.perf_fusion.time_analysis_per_video(fusionDir[i],db)
    evolution_curves.append(temp)
  
  # plot time evolution curve
  labels=scoresDir+fusionDir
  for i in range(len(labels)): 
    labels[i]=labels[i][7:]  
 
  ml.perf_fusion.plot_evolution(evolution_curves,labels)  

if __name__ == '__main__':
  main()
  



