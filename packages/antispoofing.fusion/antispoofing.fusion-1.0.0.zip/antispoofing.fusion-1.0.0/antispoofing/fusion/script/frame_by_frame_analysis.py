#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import os, sys
import argparse
import numpy

import bob
from .. import ml
from ..fusion import fusion
import antispoofing.utils.db 

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  outputDir='results/frame_based'  
      
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the scores of different countermeasures', nargs='+')
  
  parser.add_argument('-f', '--fusion-dir', type=str, dest='fusionDir', default='', help='Base directory containing the scores of different fusion strategies', nargs='+')  
  
  parser.add_argument('-e', '--end', action='store_true', default=False, help='Arg split')
    
  antispoofing.utils.db.Database.create_parser(parser, 'video')
  args = parser.parse_args()    
  
  #getting the parser variables
  scoresDir          = args.scoresDir
  fusionDir          = args.fusionDir
  
  sys.stdout.write('Printing results using ALL countermeasures...')
  sys.stdout.flush()
  
  # computing results
  tbl=[]
  tbl.append("\n\nAnalysis using ALL countermeasures:")
  tbl.append("\nPerformance of individual countermeasures:")

  for i in range(len(scoresDir)): 
    tbl=tbl+ml.perf_fusion.show_results(scoresDir[i])

  tbl.append("\nPerformance of different fusion strategies "+":")
  for i in range(len(fusionDir)): 
    tbl=tbl+ml.perf_fusion.show_results(fusionDir[i])
  
  print 'done.'
  
  # write results in text file  
  if not os.path.exists(outputDir): # if the output directory doesn't exist, create it
    bob.db.utils.makedirs_safe(outputDir)
  txt = ''.join([k+'\n' for k in tbl])

  tf = open(os.path.join(outputDir,"results.txt"), 'w')
  tf.write(txt)
  
if __name__ == '__main__':
  main()
  



