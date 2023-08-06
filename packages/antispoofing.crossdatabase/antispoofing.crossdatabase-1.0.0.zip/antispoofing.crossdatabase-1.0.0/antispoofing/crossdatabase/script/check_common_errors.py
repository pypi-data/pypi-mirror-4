#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Oct 25 19:00:48 CEST 2012

"""
This script checks the number of common errors between two face verification algorithms.

"""

import os, sys
import argparse
import bob
import numpy

import antispoofing

from antispoofing.utils.db import *
from antispoofing.utils.ml import *
from antispoofing.utils.helpers import *
from antispoofing.utils.fusion import *
from antispoofing.crossdatabase.helpers import *

import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as mpl


def eval_threshold(scorefile):
  """ finds EER threshold using the scores in the provided scorefile """
  # load the 4 column file 
  pos = []; neg = []
  lines = file(scorefile).readlines()
  line_counter = 0
  for line in lines:
    line_counter += 1
    #sys.stdout.write("Processing line [%d/%d] \n" % (line_counter, len(lines)))
    words = line.split()
    if words[0] == words[1]: pos.append(float(words[3]))
    else:neg.append(float(words[3]))
  thr = bob.measure.eer_threshold(numpy.array(neg), numpy.array(pos))
  return thr


def get_labels(indir, files, protocol, client_id=None, onlyValidScores=True):
  """
  Return a numpy.array with the labels of all xbob.db.replay.File

  @param indir The input directory where the score files are stored. They need to be checked for labeling together with the filename, in order to determine the number of valid scores in each file 
  @param files The files that need to be labeled
  @param protocol The protocol: "licit" or "spoof"
  @param client_id The id of the client if the protocol is "licit", otherwise can be left to None
  @param onlyValidScores if True will return list of labels of only the valid scores in the files
  """

  def reshape(scores):
    if(scores.shape[1]==1):
      scores = numpy.reshape(scores,(scores.shape[1],scores.shape[0]))

    return scores  

  #Findng the number of elements (total number of scores in all the files)
  totalScores = 0
  for f in files:
    if protocol == 'licit':
      fileName = str(f.make_path(os.path.join(indir, client_id), extension='.hdf5'))
    else: #'spoof' protocol
      fileName = str(f.make_path(indir,extension='.hdf5'))
    scores = bob.io.load(fileName)
    scores = reshape(scores)
    totalScores =totalScores + scores.shape[1]
    
  # calculating the labels
  allLabels = numpy.ndarray((totalScores), 'int')
  allScores = numpy.zeros(shape=(totalScores))
  offset = 0
  for f in files:
    if protocol == 'licit':
      fileName = str(f.make_path(os.path.join(indir, client_id),extension='.hdf5'))
    else: #'spoof' protocol
      fileName = str(f.make_path(indir,extension='.hdf5'))
    scores = bob.io.load(fileName)
    scores = reshape(scores)
    labels = numpy.ndarray(scores.shape, 'int')
    if protocol == 'licit':
      if client_id == "client%03d" % f.get_client_id():
        labels[0,:] = 1
      else:
        labels[0,:] = 0
    else: # 'spoof' protocol
      if f.is_real():
        labels[0,:] = 1
      else:
        labels[0,:] = 0
    
    allScores[offset:offset+scores.shape[1]] = numpy.reshape(scores,(scores.shape[1]))
    allLabels[offset:offset+labels.shape[1]] = numpy.reshape(labels,(labels.shape[1]))
    offset = offset + labels.shape[1]

  if(onlyValidScores):
    allLabels = allLabels[(numpy.where(numpy.isnan(allScores)==False))[0]]

  return allLabels


def main():

  #basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  #FEATURES_DIR = os.path.join(basedir, 'features')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresdir', default='', help='Base directory containing the scores of differenen algorithm', nargs='+')

  parser.add_argument('-t', '--threshold-file', type=str, dest='thrfile', default='', help='4-column format files with development data from where the thresholds for each of the methods can be computed', nargs='+')

  parser.add_argument('-p', '--fv-protocol', type=str, dest='faceverif_protocol', default='licit', choices=('licit','spoof'), help='The face verification protocol whose score you want to fuse')
  
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
 
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
  if len(args.scoresdir) != len(args.thrfile): 
    raise Exception("The number of provided score directories and the number of provided threshold files need to be different\n")
 
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)

  train_real, train_attack = database.get_train_data()
  devel_real, devel_attack = database.get_devel_data()
  test_real, test_attack   = database.get_test_data()
  
  #for args.faceverif_protocol == "licit", we don't need the attack data, we can just discard them. The train data we don't need in any case
  del train_real; del train_attack
  if args.faceverif_protocol == "licit":
    del devel_attack
    del test_attack
  
  # find the ID's of the clients in the subsets
  devel_clients = list(set(["client%03d" % x.get_client_id() for x in devel_real]))
  test_clients = list(set(["client%03d" % x.get_client_id() for x in test_real]))
  
  # evaluate the thresholds for the algorithms
  thresholds = [eval_threshold(thrfile) for thrfile in args.thrfile] # evaluate all the threshold
  
  # First process the devel data
  if args.faceverif_protocol == "licit": # in this case we need to iterate over all clients anc check the scores for all of them separately
    total_dev_real_ce = 0; total_dev_real_ne  = numpy.zeros((len(args.scoresdir)))
    total_test_real_ce = 0; total_test_real_ne  = numpy.zeros((len(args.scoresdir)), 'int')

    for cl in devel_clients:
      sys.stdout.write("Processing [%s/%d] in devel set\n" % (cl, len(devel_clients)))
      # creating the scores readers from different face verification algorithms
      devel_real_scorereader = ScoreFusionReader(devel_real, [os.path.join(sd, cl) for sd in args.scoresdir])
      labels = get_labels(args.scoresdir[0], devel_real, protocol='licit', client_id=cl, onlyValidScores=True)
      scoreFusion = ScoreFusion()
      dev_real_ce, dev_real_ne= scoreFusion.countCommonErrors(devel_real_scorereader, thresholds, labels)
      total_dev_real_ce += dev_real_ce; total_dev_real_ne += dev_real_ne; #total_dev_real_rce += dev_real_rce

    for cl in test_clients:
      sys.stdout.write("Processing [%s/%d] in test set\n" % (cl, len(test_clients)))
      test_real_scorereader = ScoreFusionReader(test_real, [os.path.join(sd, cl) for sd in args.scoresdir])
      labels = get_labels(args.scoresdir[0], test_real, protocol='licit', client_id=cl, onlyValidScores=True)
      scoreFusion = ScoreFusion()
      test_real_ce, test_real_ne = scoreFusion.countCommonErrors(test_real_scorereader, thresholds, labels)
      total_test_real_ce += test_real_ce; total_test_real_ne += test_real_ne; #total_test_real_rce += test_real_rce

    # calculate common errors relative to number of errors (can be skipped)
    total_dev_real_rce = float(total_dev_real_ce) / total_dev_real_ne
    total_test_real_rce = float(total_test_real_ce) / total_test_real_ne

    # write output
    res = ["Counting Common errors: " + args.faceverif_protocol.upper() + ' protocol\n']
    res.append("Development set:\n")
    res.append("Common errors: %d\n" % total_dev_real_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(total_dev_real_ne[0]), int(total_dev_real_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (total_dev_real_rce[0], total_dev_real_rce[1]))
    res.append("===================================================================\n")
    res.append("Test set:\n")
    res.append("Common errors: %d\n" % total_test_real_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(total_test_real_ne[0]), int(total_test_real_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (total_test_real_rce[0], total_test_real_rce[1]))
    print '[%s]' % ' '.join(map(str, res))     

  else: # args.faceverif_protocol == "spoof"
    # creating the scores readers from different face verification algorithms
    sys.stdout.write("Processing files in SPOOF protocol\n")
    devel_real_scorereader = ScoreFusionReader(devel_real, args.scoresdir)
    test_real_scorereader = ScoreFusionReader(test_real, args.scoresdir)
    devel_attack_scorereader = ScoreFusionReader(devel_attack, args.scoresdir)
    test_attack_scorereader = ScoreFusionReader(test_attack, args.scoresdir)

    devel_real_labels = get_labels(args.scoresdir[0], devel_real, protocol='spoof', onlyValidScores=True)
    test_real_labels = get_labels(args.scoresdir[0], test_real, protocol='spoof', onlyValidScores=True)
    devel_attack_labels = get_labels(args.scoresdir[0], devel_attack, protocol='spoof', onlyValidScores=True)
    test_attack_labels = get_labels(args.scoresdir[0], test_attack, protocol='spoof', onlyValidScores=True)

    scoreFusion = ScoreFusion()
    dev_real_ce, dev_real_ne= scoreFusion.countCommonErrors(devel_real_scorereader, thresholds, devel_real_labels)
    test_real_ce, test_real_ne = scoreFusion.countCommonErrors(test_real_scorereader, thresholds, test_real_labels)
    dev_attack_ce, dev_attack_ne = scoreFusion.countCommonErrors(devel_attack_scorereader, thresholds, devel_attack_labels)
    test_attack_ce, test_attack_ne = scoreFusion.countCommonErrors(test_attack_scorereader, thresholds, test_attack_labels)

    #calculate common errors relative to number of errors (can be skipped)
    dev_real_rce = float(numpy.array(dev_real_ce)) / numpy.array(dev_real_ne)
    dev_attack_rce = float(numpy.array(dev_attack_ce)) / numpy.array(dev_attack_ne)
    test_real_rce = float(numpy.array(test_real_ce)) / numpy.array(test_real_ne)
    test_attack_rce = float(numpy.array(test_attack_ce)) / numpy.array(test_attack_ne)
  
    # write output
    res = ["Counting Common errors:" + args.faceverif_protocol.upper() + '\n']
    res.append("Development set - REAL ACCESSES:\n")
    res.append("Common errors: %d\n" % dev_real_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(dev_real_ne[0]), int(dev_real_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (dev_real_rce[0], dev_real_rce[1]))
    res.append("----------------------------------------------------------\n")
    res.append("Development set - SPOOFING ATTACKS:\n")
    res.append("Common errors: %d\n" % dev_attack_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(dev_attack_ne[0]), int(dev_attack_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (dev_attack_rce[0], dev_attack_rce[1]))
    res.append("===========================================================\n")
    res.append("Test set- REAL ACCESSES:\n")
    res.append("Common errors: %d\n" % test_real_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(test_real_ne[0]), int(test_real_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (test_real_rce[0], test_real_rce[1]))
    res.append("----------------------------------------------------------\n")
    res.append("Test set- SPOOFING ATTACKS:\n")
    res.append("Common errors: %d\n" % test_attack_ce)
    res.append("Number of errors: alg1 - %d; alg2 - %d\n" % (int(test_attack_ne[0]), int(test_attack_ne[1])))
    res.append("Relative common errors: alg1 - %.3f; alg2 - %.3f\n" % (test_attack_rce[0], test_attack_rce[1]))
    print '[%s]' % ' '.join(map(str, res)) 
    

if __name__ == "__main__":
  main()




