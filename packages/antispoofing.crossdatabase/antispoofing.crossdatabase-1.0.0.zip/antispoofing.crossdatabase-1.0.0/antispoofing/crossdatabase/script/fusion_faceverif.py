#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed Oct 31 14:47:51 CET 2012

"""
This script performs fusion of two or more face verification systems. It writes the fued scores into a specified output directory

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


def save_fused_scores(all_scores, all_labels, dirname, protocol, subset):
  """Saves the fused scores in a 4 column format. Since the exact identity of the user is not known, as well as the filename of the used file, we will put dummy identities and dummy filename in the first three columns"""

  outdir = os.path.join(dirname, "10_" + protocol, "nonorm")
  filename = "scores-" + subset
  utils.ensure_dir(outdir)
  f = open(os.path.join(outdir, filename), 'w')
  for i in range(0, len(all_scores)):
    if all_labels[i] == 0: # negative (imposter or spoof, depending on the protocol)
      f.write("x y foo %f\n" % all_scores[i])
    else: # positive sample, real access
      f.write("x x foo %f\n" % all_scores[i])
  f.close()


def main():

  #basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  #FEATURES_DIR = os.path.join(basedir, 'features')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresdir', default='', help='Base directory containing the scores of different algorithms', nargs='+')

  parser.add_argument('-p', '--fv-protocol', type=str, dest='faceverif_protocol', default='licit', choices=('licit','spoof'), help='The face verification protocol whose score you want to fuse')
  
  parser.add_argument('-f', '--score-fusion', type=str, dest='fusionalg', default='LLR', choices=('LLR','SUM'), help='The score fusion algorithm')

  parser.add_argument('-o', '--output-dir', type=str, dest='outputdir', default='', help='Base directory that will be used to save the fused scores.')
  
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
 
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
 
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
  
  # read the training scores (needed for training the LLR machine) - reading them from a separate file where they are stated
  train_pos = bob.io.load(os.path.join(args.scoresdir[0], "scores_train_pos.hdf5"))
  train_neg = bob.io.load(os.path.join(args.scoresdir[0], "scores_train_neg.hdf5"))
  all_train_pos = numpy.reshape(train_pos, (len(train_pos),1))
  all_train_neg = numpy.reshape(train_neg, (len(train_neg),1))
  if args.fusionalg == 'LLR':
    for d in args.scoresdir[1:len(args.scoresdir)]:
      train_pos = bob.io.load(os.path.join(d, "scores_train_pos.hdf5"))
      train_neg = bob.io.load(os.path.join(d, "scores_train_neg.hdf5"))
      all_train_pos = numpy.append(all_train_pos, numpy.reshape(train_pos, (len(train_pos),1)), axis=1)
      all_train_neg = numpy.append(all_train_neg, numpy.reshape(train_neg, (len(train_neg),1)), axis=1)  
  
  # First process the devel data
  if args.faceverif_protocol == "licit": # in this case we need to iterate over all clients and fuse the scores for each of them separately

    all_devel_real_scores = numpy.ndarray((0), 'float'); all_devel_real_labels = numpy.ndarray((0), 'int');
    for cl in devel_clients:
      sys.stdout.write("Processing [%s/%d] in devel set\n" % (cl, len(devel_clients)))
      # creating the scores readers from different face verification algorithms
      devel_real_scorereader = ScoreFusionReader(devel_real, [os.path.join(sd, cl) for sd in args.scoresdir])
      labels = get_labels(args.scoresdir[0], devel_real, protocol='licit', client_id=cl, onlyValidScores=True)
      scoreFusion = ScoreFusion()
      if args.fusionalg == "LLR":
        devel_real_fused = scoreFusion.getLLRScores(devel_real_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
      elif args.fusionalg == "SUM":
        devel_real_fused = scoreFusion.getSUMScores(devel_real_scorereader, normalizeOutput = False)
      all_devel_real_scores = numpy.append(all_devel_real_scores, devel_real_fused, axis=0) # append scores from all clients
      all_devel_real_labels = numpy.append(all_devel_real_labels, labels, axis = 0) # append labels from all clients
    save_fused_scores(all_devel_real_scores, all_devel_real_labels, args.outputdir, protocol = "licit", subset = "dev") # save the scores in 4-column format
    

    all_test_real_scores = numpy.ndarray((0), 'float'); all_test_real_labels = numpy.ndarray((0), 'int');
    for cl in test_clients:
      sys.stdout.write("Processing [%s/%d] in test set\n" % (cl, len(test_clients)))
      test_real_scorereader = ScoreFusionReader(test_real, [os.path.join(sd, cl) for sd in args.scoresdir])
      labels = get_labels(args.scoresdir[0], test_real, protocol='licit', client_id=cl, onlyValidScores=True)
      scoreFusion = ScoreFusion()
      if args.fusionalg == "LLR":
        test_real_fused = scoreFusion.getLLRScores(test_real_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
      elif args.fusionalg == "SUM":
        test_real_fused = scoreFusion.getSUMScores(test_real_scorereader, normalizeOutput = False)
      all_test_real_scores = numpy.append(all_test_real_scores, test_real_fused, axis=0) # append scores from all clients
      all_test_real_labels = numpy.append(all_test_real_labels, labels, axis = 0) # append labels from all clients
    save_fused_scores(all_test_real_scores, all_test_real_labels, args.outputdir, protocol = "licit", subset = "eval") # save the scores in 4-column format    

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
    if args.fusionalg == "LLR":
      devel_real_fused = scoreFusion.getLLRScores(devel_real_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
      test_real_fused = scoreFusion.getLLRScores(test_real_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
      devel_attack_fused = scoreFusion.getLLRScores(devel_attack_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
      test_attack_fused = scoreFusion.getLLRScores(test_attack_scorereader, normalizeOutput = False, trainScores = (all_train_pos, all_train_neg))
    elif args.fusionalg == "SUM":
      devel_real_fused = scoreFusion.getSUMScores(devel_real_scorereader, normalizeOutput = False)
      test_real_fused = scoreFusion.getSUMScores(test_real_scorereader, normalizeOutput = False)
      devel_attack_fused = scoreFusion.getSUMScores(devel_attack_scorereader, normalizeOutput = False)
      test_attack_fused = scoreFusion.getSUMScores(test_attack_scorereader, normalizeOutput = False)

    save_fused_scores(numpy.append(devel_real_fused, devel_attack_fused, axis = 0), numpy.append(devel_real_labels, devel_attack_labels), args.outputdir, protocol = "spoof", subset = "dev") # save the devel scores in 4-column format
    save_fused_scores(numpy.append(test_real_fused, test_attack_fused, axis = 0), numpy.append(test_real_labels, test_attack_labels), args.outputdir, protocol = "spoof", subset = "eval") # save the devel scores in 4-column format
    

if __name__ == "__main__":
  main()




