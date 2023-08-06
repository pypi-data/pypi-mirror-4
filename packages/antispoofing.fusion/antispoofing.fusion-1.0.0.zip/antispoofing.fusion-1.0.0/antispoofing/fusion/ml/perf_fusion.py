import os
import sys
import bob
import xbob.db.replay as replay
import numpy

import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
import matplotlib.pyplot as mpl
import matplotlib.colors as colors
import matplotlib.cm as cmx

def decisions(score_dir,objects,thres):

  decisions = []

  #for key, filename in files.items():
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(score_dir, '.hdf5'))
    scores = bob.io.load(str(filename)).ravel()
    
    running_scores=[]
    running_dec = []
    
    #score average
    for frame_nr in range(0,230):
      if not numpy.isnan(scores[frame_nr]):
        running_scores.append(scores[frame_nr])
      if not running_scores:
		    dec=0
      else:		  
        if numpy.mean(numpy.array(running_scores)) < thres: dec = -1
        else: dec=1
      running_dec.append(dec)
    """
    #decision average
    for frame_nr in range(0,230):
      if not numpy.isnan(scores[frame_nr]):
        if scores[frame_nr] < thres: dec = -1
        else: dec=1
        running_scores.append(dec)
      if not running_scores:
		    dec=0
      else: 
        if numpy.mean(numpy.array(running_scores)) < 0: dec = -1
        else: dec=1
      running_dec.append(dec)
    """  
    decisions.append(running_dec)		
    
  return decisions
	
def frfa_list(real, attack, real_decisions, attack_decisions):
  """Returns a list composed of the false rejections and false accepts"""

  fr = []
  fa = []

  first=numpy.where(numpy.array(real_decisions[0]) != 0)[0][0]

  for k in range(first, 230):    
    fr_k = [] #false rejections for k=k
    for i, rd in enumerate(real_decisions):
      if rd[k] <= 0: fr_k.append(real[i])
    fa_k = [] #false accepts for k=k
    for i, ad in enumerate(attack_decisions):
      if ad[k] >= 0: fa_k.append(attack[i])
    fr.append(fr_k)
    fa.append(fa_k)

  return fr, fa,first
	
def errors_evolution(real_files, attack_files,fr,fa,first):
  d = {}
  for i, (fr, fa) in enumerate(zip(fr, fa)):
      #realtime = (i*(windowsize-overlap)) + windowsize
    realtime=i+first
    d[realtime] = {}
    d[realtime]['frr'] = 100*float(len(fr))/len(real_files)
    d[realtime]['fr'] = fr
    d[realtime]['far'] = 100*float(len(fa))/len(attack_files)
    d[realtime]['fa'] = fa
    d[realtime]['hter'] = 0.5 * (d[realtime]['far'] + d[realtime]['frr'])

  return d

def plot_evolution(pdffilename,d):
    """Creates a plot showing the FAR, FRR and HTER time evolution"""      

    x = sorted(d.keys())
    far = [d[k]['far'] for k in x] 
    frr = [d[k]['frr'] for k in x] 
    hter = [d[k]['hter'] for k in x] 

    mpl.plot(x, far, color='black', alpha=0.4, dashes=(6,2),linestyle='dashed', label='Avg.FAR')
    mpl.plot(x, frr, color='black', linestyle=':', label='Avg.FRR')
    mpl.plot(x, hter, color='black', label='Avg.HTER')
    mpl.title('Performance evolution of the combined score')
    mpl.xlabel('Frames')
    mpl.ylabel('Error')
    mpl.grid(True, alpha=0.4)
    mpl.legend()
    mpl.savefig(pdffilename)
    mpl.clf()

def plot_evolution_hter(pdffilename,d,label,color,style):
    """Creates a plot showing the FAR, FRR and HTER time evolution"""      
  
    x = sorted(d.keys())
    hter = [d[k]['hter'] for k in x] 

    mpl.plot(x, hter, color=color, label=label,linestyle=style)
    mpl.title('Performance evolution of the combined score')
    mpl.xlabel('Frames')
    mpl.ylabel('Error')
    mpl.grid(True, alpha=0.4)
    mpl.legend()
    mpl.savefig(pdffilename)

def write_table(file,d):
    """Writes a nicely formatted table containing the time-analysis"""
    use=d
    def print_max(value, fmt, maxlength):
      v = fmt % k
      if len(v) > maxlength: maxlength = len(v)
      return v, maxlength

    txt = {}
    max_frame = 0
    max_far = 0
    max_fa = 0
    max_frr = 0
    max_fr = 0
    max_hter = 0
    for k in use.keys():
      txt[k] = {}
      txt[k]['frame'], max_frame = print_max(k, '%d', max_frame)
      txt[k]['frr'], max_frr = print_max(use[k]['frr'], '%.2f%%', max_frr)
      txt[k]['fr'], max_fr = print_max(len(use[k]['fr']), '%d', max_fr)
      txt[k]['far'], max_far = print_max(use[k]['far'], '%.2f%%', max_far)
      txt[k]['fa'], max_fa = print_max(len(use[k]['fa']), '%d', max_fa)
      txt[k]['hter'], max_hter = print_max(use[k]['hter'], '%.2f%%', max_hter)

    spacing = 1

    frame_size = max(max_frame, len('Frame'))
    frr_size = max(max_frr, len('FRR'))
    fr_size = max(max_fr, len('#FR'))
    far_size = max(max_far, len('FAR'))
    fa_size = max(max_fa, len('#FA'))
    hter_size = max(max_hter, len('HTER'))

    sizes = [
      (frame_size+2*spacing),
      (frr_size+2*spacing),
      (fr_size+2*spacing),
      (far_size+2*spacing),
      (fa_size+2*spacing),
      (hter_size+2*spacing),
      ]

    hline = [k*'=' for k in sizes]
    header = [
      'Frame'.center(sizes[0]),
      'FRR'.center(sizes[1]),
      '#FR'.center(sizes[2]),
      'FAR'.center(sizes[3]),
      '#FA'.center(sizes[4]),
      'HTER'.center(sizes[5]),
      ]

    file.write(' '.join(hline) + '\n')
    file.write(' '.join(header) + '\n')
    file.write(' '.join(hline) + '\n')

    curr_fr = -1
    curr_fa = -1
    first_time = True
    for k in sorted(use.keys()):
      if curr_fr == len(use[k]['fr']) and curr_fa == len(use[k]['fa']):
        if first_time:
          data = [
            '...'.center(sizes[0]),
            '...'.center(sizes[1]),
            '...'.center(sizes[2]),
            '...'.center(sizes[3]),
            '...'.center(sizes[4]),
            '...'.center(sizes[5]),
            ]
          file.write(' '.join(data) + '\n')
          first_time = False
      else:
        data = [
          ('%d' % k).rjust(sizes[0]-2*spacing).center(sizes[0]),
          ('%.2f%%' % use[k]['frr']).rjust(sizes[1]-2*spacing).center(sizes[1]),
          ('%d' % len(use[k]['fr'])).rjust(sizes[2]-2*spacing).center(sizes[2]),
          ('%.2f%%' % use[k]['far']).rjust(sizes[3]-2*spacing).center(sizes[3]),
          ('%d' % len(use[k]['fa'])).rjust(sizes[4]-2*spacing).center(sizes[4]),
          ('%.2f%%' % use[k]['hter']).rjust(sizes[5]-2*spacing).center(sizes[5]),
          ]
        file.write(' '.join(data) + '\n')

        # reset
        curr_fr = len(use[k]['fr'])
        curr_fa = len(use[k]['fa'])
        first_time = True
    
    file.write(' '.join(hline) + '\n')

def calc_and_print_results(devel_attack_out,devel_real_out,test_attack_out,test_real_out,case,evo):
  
  thres = bob.measure.eer_threshold(devel_attack_out, devel_real_out)
  
  dev_far, dev_frr = bob.measure.farfrr(devel_attack_out, devel_real_out, thres)
  test_far, test_frr = bob.measure.farfrr(test_attack_out, test_real_out, thres)
  
  devel_ccn = numpy.invert(bob.measure.correctly_classified_negatives(devel_attack_out,thres))
  devel_ccp = numpy.invert(bob.measure.correctly_classified_positives(devel_real_out,thres))
  test_ccn = numpy.invert(bob.measure.correctly_classified_negatives(test_attack_out,thres))
  test_ccp = numpy.invert(bob.measure.correctly_classified_positives(test_real_out,thres))
  
  tbl = []
  tbl.append(" Frame based performance under various attacks: ")
  tbl.append("  threshold: %.4f" % thres)
  tbl.append("  dev: TOTAL ERROR RATE %.2f%% | FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%%" % \
      (100*(round(dev_frr*len(devel_real_out))+round(dev_far*len(devel_attack_out)))/(len(devel_attack_out)+len(devel_real_out)),
       100*dev_far, int(round(dev_far*len(devel_attack_out))), len(devel_attack_out), 
       100*dev_frr, int(round(dev_frr*len(devel_real_out))), len(devel_real_out),
       50*(dev_far+dev_frr)))
  tbl.append("  test: TOTAL ERROR RATE %.2f%% | FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%%" % \
      (100*(round(test_frr*len(test_real_out))+round(test_far*len(test_attack_out)))/(len(test_attack_out)+len(test_real_out)),
       100*test_far, int(round(test_far*len(test_attack_out))), len(test_attack_out),
       100*test_frr, int(round(test_frr*len(test_real_out))), len(test_real_out),
       50*(test_far+test_frr)))

  txt = ''.join([k+'\n' for k in tbl])

  #print txt  
  #print ''

  return tbl
  
def get_mistakes(devel_attack_out,devel_real_out,test_attack_out,test_real_out):
  
  thres = bob.measure.eer_threshold(devel_attack_out, devel_real_out)
  
  devel_ccn = numpy.invert(bob.measure.correctly_classified_negatives(devel_attack_out,thres))
  devel_ccp = numpy.invert(bob.measure.correctly_classified_positives(devel_real_out,thres))
  test_ccn = numpy.invert(bob.measure.correctly_classified_negatives(test_attack_out,thres))
  test_ccp = numpy.invert(bob.measure.correctly_classified_positives(test_real_out,thres))

  return devel_ccn,devel_ccp,test_ccn,test_ccp

def Venn_as_numbers(fars,frrs,samples):  
  
  errorsCounter = numpy.empty(shape=(len(fars)),dtype='object')
  totalErrors  = numpy.empty(shape=(len(fars)))
  
  for i in range(len(fars)):
    labels = numpy.concatenate((fars[i],frrs[i]), axis=0)
    errorsCounter[i] = numpy.where(labels)[0]
    totalErrors[i] = len(errorsCounter[i]) 
    
  intersection=errorsCounter[0]
  histogram=numpy.histogram(errorsCounter[0],bins=range(0,samples+1))[0]
  
  for i in range(1,len(fars)):
    intersection = numpy.intersect1d(intersection,errorsCounter[i])
    hist_temp=numpy.histogram(errorsCounter[i],bins=range(0,samples+1))[0]
    histogram=histogram+hist_temp
  count=float(len(fars))/2
  ceil_count=numpy.ceil(count)  
  halffis=histogram>=ceil_count
  #print count , " --ceil--> ", ceil_count

  if ceil_count!=count:
    half_result = " More than half of the used "+ str(len(fars)) + " countermeasures were wrong " + str(len(numpy.where(halffis)[0])) + " times"
  else:
    half_result = " Half of the used "+ str(len(fars)) + " countermeasures were wrong " + str(len(numpy.where(halffis)[0])) + " times"

  tbl=[]
  tbl.append(" The used "+ str(len(fars)) + " countermeasures were all wrong " + str(len(intersection)) + " times")    
  tbl.append(" which equals to " + str(numpy.around(float(len(intersection))/samples*100, decimals=2)) + "% of all samples.")
  tbl.append(half_result)
  tbl.append(" which equals " + str(numpy.around(float(len(numpy.where(halffis)[0]))/samples*100, decimals=2)) + "% of all samples.")

  tbl.append("\n The performance of \"majority vote\" rule and best case scenario, " + str(numpy.around(float(len(numpy.where(halffis)[0]))/samples*100, decimals=2)) +"% and " + str(numpy.around(float(len(intersection))/samples*100, decimals=2)) + "%.")
  txt = ''.join([k+'\n' for k in tbl])
  
  return tbl

def show_results(method):  

  tbl=[]
  tbl.append('\n'+method[7:]+':')
  devel_attack_out=bob.io.load(method+'/devel_attack.hdf5')
  devel_real_out=bob.io.load(method+'/devel_real.hdf5')
  test_attack_out=bob.io.load(method+'/test_attack.hdf5')
  test_real_out=bob.io.load(method+'/test_real.hdf5')

  devel_attack_out=devel_attack_out.reshape(devel_attack_out.shape[0],1)
  devel_real_out=devel_real_out.reshape(devel_real_out.shape[0],1)
  
  test_attack_out=test_attack_out.reshape(test_attack_out.shape[0],1)
  test_real_out=test_real_out.reshape(test_real_out.shape[0],1)  
  
  tbl_temp=calc_and_print_results(devel_attack_out[:,0],devel_real_out[:,0],test_attack_out[:,0],test_real_out[:,0],method,1)
  tbl=tbl+tbl_temp
  
  return tbl

def time_analysis_per_video(method,db):    
    
  print '\n'+method + ':'
  
  devel_attack_out=bob.io.load(method+'/devel_attack.hdf5').ravel()
  devel_real_out=bob.io.load(method+'/devel_real.hdf5').ravel()
    
  thres = bob.measure.eer_threshold(devel_attack_out, devel_real_out)
  
  #score_dir = 'scores/' + method
  score_dir = method
  protocol='grandtest'
  
  process_devel_real, process_devel_attack = db.get_devel_data()
  process_test_real, process_test_attack = db.get_test_data()
  
  sys.stdout.write(' Analyzing the real accesses in devel set...')
  sys.stdout.flush()
  devel_real_dec = decisions(score_dir,process_devel_real,thres)
  print 'done.'
  sys.stdout.write(' Analyzing the attacks attempts in devel set...')
  sys.stdout.flush()
  devel_attack_dec = decisions(score_dir,process_devel_attack,thres)
  print 'done.'
  sys.stdout.write(' Analyzing the real accesses in test set...')
  sys.stdout.flush()
  test_real_dec = decisions(score_dir,process_test_real,thres)
  print 'done.'
  sys.stdout.write(' Analyzing the attack attempts in test set...')
  sys.stdout.flush()
  test_attack_dec = decisions(score_dir,process_test_attack,thres)
  print 'done.'
  method=method[7:]
  sys.stdout.write(' Plotting figures...')
  sys.stdout.flush()
  (dev_fr, dev_fa, first) = frfa_list(process_devel_real, process_devel_attack, devel_real_dec, devel_attack_dec)
  (test_fr, test_fa,first) = frfa_list(process_test_real, process_test_attack, test_real_dec, test_attack_dec)
  
  d_dev = errors_evolution(process_devel_real, process_devel_attack,dev_fr,dev_fa,first)
  d_test = errors_evolution(process_test_real, process_test_attack,test_fr,test_fa,first)
  
  if not os.path.exists('results/evolution'): # if the output directory doesn't exist, create it
    bob.db.utils.makedirs_safe('results/evolution')
  
  write_table(open('results/evolution/evo_devel_'+ method+'.rst', 'wt'),d_dev)
  write_table(open('results/evolution/evo_test_'+ method+'.rst', 'wt'),d_test)

  print 'done.'
  
  return d_test  

def plot_evolution(dts,labels):   
  mpl.clf()
  nCurves = len(labels)
  values = range(nCurves)
  jet = cm = mpl.get_cmap('jet') 
  cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
  scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
  for i in values: 
    colorVal = scalarMap.to_rgba(values[i])
    plot_evolution_hter(os.path.join('results/evolution/test_allin.pdf'),dts[i],labels[i],colorVal,'solid')
