#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import os, sys
import argparse
import numpy

import bob
import xbob.db.replay
from .. import ml
from ..fusion import fusion 
from ..score_fusion import *
import argparse
import antispoofing.utils.db 


def save_scores(train_real,train_attack,devel_real,devel_attack,test_real,test_attack,outputDir,db):
  
  process_train_real, process_train_attack = db.get_train_data()
  process_devel_real, process_devel_attack = db.get_devel_data()
  process_test_real, process_test_attack = db.get_test_data()  
   
  if not os.path.exists(outputDir): # if the output directory doesn't exist, create it
    bob.db.utils.makedirs_safe(outputDir)
  bob.io.save(train_attack, outputDir+'/train_attack.hdf5')
  bob.io.save(train_real, outputDir+'/train_real.hdf5')
  bob.io.save(devel_attack, outputDir+'/devel_attack.hdf5')
  bob.io.save(devel_real, outputDir+'/devel_real.hdf5')
  if process_test_attack:
    bob.io.save(test_attack, outputDir+'/test_attack.hdf5')
  bob.io.save(test_real, outputDir+'/test_real.hdf5')
 
  sys.stdout.write(' Saving scores for each video...')
  sys.stdout.flush()

  map_scores(outputDir, process_train_real, numpy.reshape(train_real, [len(train_real), 1])) 
  map_scores(outputDir, process_train_attack, numpy.reshape(train_attack, [len(train_attack), 1]))
  map_scores(outputDir, process_devel_real, numpy.reshape(devel_real, [len(devel_real), 1])) 
  map_scores(outputDir, process_devel_attack, numpy.reshape(devel_attack, [len(devel_attack), 1]))
  map_scores(outputDir, process_test_real, numpy.reshape(test_real, [len(test_real), 1]))
  if process_test_attack:
    map_scores(outputDir, process_test_attack, numpy.reshape(test_attack, [len(test_attack), 1]))
  print 'done.'  

def map_scores(score_dir, objects, score_list):
  indir='scores/valid_frames'
  num_scores = 0 # counter for how many valid frames have been processed so far in total of all the objects

  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    vf = bob.io.load(filename)
    vf_indices = list(numpy.where(vf == 1)[0]) # indices of the valid frames of the object
    nvf_indices = list(numpy.where(vf == 0)[0]) # indices of the invalid frames of the object
    scores = numpy.ndarray((len(vf), 1), dtype='float64') 
    scores[vf_indices] = score_list[num_scores:num_scores + len(vf_indices)] # set the scores of the valid frames
    scores[nvf_indices] = numpy.NaN # set NaN for the scores of the invalid frames
    num_scores += len(vf_indices) # increase the nu,ber of valid scores that have been already maped
    obj.save(scores, score_dir, '.hdf5') # save the scores

def main():
          
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the scores of different countermeasures', nargs='+')  
  
  parser.add_argument('-o', '--output-dir', type=str, dest='outputDir', default='', help='Base directory that will be used to save the fused scores.')
   
  ScoreFusion.create_parser(parser)
  antispoofing.utils.db.Database.create_parser(parser, 'video')
  args = parser.parse_args()    
  
  # getting the parser variables
  scoresDir          = args.scoresDir
  outputDir          = args.outputDir  
  
  db = args.cls(args) 
  real_train_scores,attack_train_scores=fusion.load_scores('train',scoresDir)
  real_devel_scores,attack_devel_scores=fusion.load_scores('devel',scoresDir)
  real_test_scores,attack_test_scores=fusion.load_scores('test',scoresDir)  
  
  # combine training scores of real accesses and attacks for score normalization
  data_to_normalization = numpy.concatenate((real_train_scores,attack_train_scores),axis=0)  
  
  # perform score fusion on all subsets...
  
  print 'Score fusion using:',args.fusion_alg, 'with', args.normalizer, ':'
  
  score_fusion = ScoreFusion.load(args,data_to_normalization)
  score_fusion.train([real_train_scores,attack_train_scores])
    
  train_real = score_fusion(real_train_scores)
  train_attack = score_fusion(attack_train_scores)
    
  devel_real = score_fusion(real_devel_scores)
  devel_attack = score_fusion(attack_devel_scores)

  test_real = score_fusion(real_test_scores)
  test_attack = score_fusion(attack_test_scores)
 
  # ...and save scores for future use
  save_scores(train_real,train_attack,devel_real,devel_attack,test_real,test_attack,outputDir,db)
   
if __name__ == '__main__':
  main()
