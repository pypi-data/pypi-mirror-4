import os
import sys
import bob
import numpy
import antispoofing.utils.db 

def create_full_dataset(indir, sync_dir, objects,fileout):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = None

  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    fvs = bob.io.load(filename)
    if fvs.shape[1] > fvs.shape[0]:   
      fvs = fvs.reshape(fvs.shape[1],fvs.shape[0])
    filename = os.path.expanduser(obj.make_path(sync_dir, '.hdf5'))
    valid = bob.io.load(filename)
    
    ind=numpy.where(valid==0)

    fvs = numpy.delete(fvs,ind[0],axis=0)

    if dataset is None:
      dataset = fvs
    else:
      dataset = numpy.append(dataset, fvs, axis = 0)

  bob.io.save(dataset, os.path.join(indir,fileout))

def process_valid_scores(indir, sync_dir, objects,fileout):

  sys.stdout.write(' Finding valid frames...')
  sys.stdout.flush()
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir[0], '.hdf5'))
    vf = bob.io.load(filename)
    if vf.shape[1] > vf.shape[0]:   
      vf = vf.reshape(vf.shape[1],vf.shape[0])
    find_valid=numpy.invert(numpy.isnan(vf))
    for i in range(1,len(indir)): 

      filename = os.path.expanduser(obj.make_path(indir[i], '.hdf5'))
      vf = bob.io.load(filename)     
          
      if vf.shape[1] > vf.shape[0]:   
        vf = vf.reshape(vf.shape[1],vf.shape[0])
        
      find_valid = numpy.logical_and(find_valid,numpy.invert(numpy.isnan(vf)))
    
    valid_frames = numpy.zeros((len(vf), 1), dtype='float64')
    
    valid_frames[find_valid]=1
    
    obj.save(valid_frames, sync_dir, '.hdf5') # save the scores
  print 'done.'  

  sys.stdout.write(' Constructing synchronized score lists...')
  sys.stdout.flush()
  for i in range(0,len(indir)):
    create_full_dataset(indir[i], sync_dir, objects,fileout)
  
  print 'done.'
    
def sync_data(indir,db):
  
  sync_dir='scores/valid_frames'

  process_train_real, process_train_attack = db.get_train_data()
  process_devel_real, process_devel_attack = db.get_devel_data()
  process_test_real, process_test_attack = db.get_test_data()  

    
  print '\ntrain real:'
  process_valid_scores(indir, sync_dir, process_train_real,'train_real.hdf5')
  print 'train attack:'
  process_valid_scores(indir, sync_dir, process_train_attack,'train_attack.hdf5')
  print 'devel_real:'
  process_valid_scores(indir, sync_dir, process_devel_real,'devel_real.hdf5')
  print 'devel_attack:'
  process_valid_scores(indir, sync_dir, process_devel_attack,'devel_attack.hdf5')
  print 'test_real:'
  process_valid_scores(indir, sync_dir, process_test_real,'test_real.hdf5')
  print 'test attack:'
  process_valid_scores(indir, sync_dir, process_test_attack,'test_attack.hdf5')


def load_scores(subset,indir):
  

  real_out=bob.io.load(indir[0]+'/'+subset+'_real.hdf5')
  attack_out=bob.io.load(indir[0]+'/'+subset+'_attack.hdf5')    
  
  for i in range(1,len(indir)):
    real_out=numpy.append(real_out, bob.io.load(indir[i]+'/'+subset+'_real.hdf5'), axis=1)
    attack_out=numpy.append(attack_out, bob.io.load(indir[i]+'/'+subset+'_attack.hdf5'), axis=1)      

  return real_out,attack_out
 
def Venn_analysis(scoreDir):
  
  from .. import ml  
  devel_real_out,devel_attack_out=load_scores('devel',scoreDir)
  test_real_out,test_attack_out=load_scores('test',scoreDir)
  
  tbl=[]
  # calculation of the error rates
  devel_fars=[]
  devel_frrs=[]
  test_fars=[]
  test_frrs=[]
  
  for i in range(devel_real_out.shape[1]):
    devel_far,devel_frr,test_far,test_frr = ml.perf_fusion.get_mistakes(devel_attack_out[:,i],devel_real_out[:,i],test_attack_out[:,i],test_real_out[:,i])    

    devel_fars.append(devel_far)
    devel_frrs.append(devel_frr)
    test_fars.append(test_far)
    test_frrs.append(test_frr)
  #print ' '
  #print 'DEVEL:'
  tbl_temp=ml.perf_fusion.Venn_as_numbers(devel_fars,devel_frrs,devel_real_out.shape[0]+devel_attack_out.shape[0])
  tbl.append(' DEVEL:')
  tbl=tbl+tbl_temp
  #print ' TEST:'
  tbl_temp=ml.perf_fusion.Venn_as_numbers(test_fars,test_frrs,test_real_out.shape[0]+test_attack_out.shape[0])  
  tbl.append('\n TEST:')
  tbl=tbl+tbl_temp
  
  return tbl
  

