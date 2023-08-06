#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import os, sys
import argparse
import numpy

import bob
import antispoofing.utils.db 
from ..fusion import fusion

def main():
 
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the scores of different countermeasures', nargs='+')  
  
  parser.add_argument('-e', '--end', action='store_true', default=False, help='Arg split')
  
  antispoofing.utils.db.Database.create_parser(parser, 'video')
  args = parser.parse_args()

  # getting the parser variables
  scoresDir = args.scoresDir
  db = args.cls(args) 
  
  print '\nScore folders:'
  for i in range(len(scoresDir)):
    print scoresDir[i]
  
  # synchronize scores
  print '\nSynchronizing output scores between ALL countermeasures...'
  fusion.sync_data(scoresDir,db)   
  
if __name__ == '__main__':
  main()
