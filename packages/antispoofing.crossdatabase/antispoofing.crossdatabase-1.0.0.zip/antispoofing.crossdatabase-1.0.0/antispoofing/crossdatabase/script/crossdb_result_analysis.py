#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Jul 27 14:30:00 CEST 2012

"""
This script will run the result analisys
"""

import os, sys
import argparse
import bob
import numpy

from antispoofing.crossdatabase.helpers import *

from antispoofing.utils.ml import *
from antispoofing.utils.helpers import *
from antispoofing.utils.db import *
from antispoofing.lbptop.helpers import *


def main():

  available_dbs = get_db_names()

  ##########
  # General configuration
  ##########

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the Scores to a specific protocol  (defaults to "%(default)s")')

  #parser.add_argument('-n','--score-normalization',type=str, dest='scoreNormalization',default='', choices=('znorm','minmax',''))

  #parser.add_argument('-t', '--thresholds', type=float, dest='thresholds', default=[], help='The predifined thresholds', nargs='+')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  parser.add_argument('-a', '--average-scores', action='store_true', dest='average_scores', default=False, help='Use the average of scores')

  parser.add_argument('-i', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')


  parser.add_argument('-d', '--dev-set', type=str, dest='dev_set', default=available_dbs[0], choices=available_dbs, help='The database used in the devel set')

  parser.add_argument('-t', '--test-set', type=str, dest='test_set', default=available_dbs[0], choices=available_dbs, help='The database used in the test set')

  args = parser.parse_args()


  ## Parsing
  scoresDir          = args.scoresDir
  #outputDir          = args.outputDir
  verbose            = args.verbose
  average_scores     = args.average_scores
  average_size       = args.average_size

  #Loading databases
  devDB  = get_db_by_name(args.dev_set)
  testDB = get_db_by_name(args.test_set)


  if not os.path.exists(scoresDir):
    parser.error("scores-dir directory does not exist")

  #if not os.path.exists(outputDir): # if the output directory doesn't exist, create it
    #bob.db.utils.makedirs_safe(outputDir)


  #########
  # Loading some dataset
  #########
  if(verbose):
    print("Querying the database ... ")

  tuneReal, tuneAttack = devDB.get_devel_data()

  develReal, develAttack = testDB.get_devel_data()
  testReal, testAttack   = testDB.get_test_data()

  if(verbose):
    print("Generating test results ....")


  #Getting the scores

  #Tunning (dev) set D1
  realScores   = ScoreReader(tuneReal,scoresDir)
  attackScores = ScoreReader(tuneAttack,scoresDir)
  tune_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  tune_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)


  #Devel set D2
  realScores   = ScoreReader(develReal,scoresDir)
  attackScores = ScoreReader(develAttack,scoresDir)
  devel_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  devel_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)


  #Test set D2
  realScores   = ScoreReader(testReal,scoresDir)
  attackScores = ScoreReader(testAttack,scoresDir)
  test_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  test_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)

  #if numpy.mean(devel_real_scores) < numpy.mean(devel_attack_scores):
    #train_real_scores = train_real_scores * -1; train_attack_scores = train_attack_scores * -1
    #devel_real_scores = devel_real_scores * -1; devel_attack_scores = devel_attack_scores * -1
    #test_real_scores = test_real_scores * -1; test_attack_scores = test_attack_scores * -1


  #Defining threshold
  thres  = bob.measure.eer_threshold(tune_attack_scores,tune_real_scores)

  #EER on the tune set
  far,frr = bob.measure.farfrr(tune_attack_scores, tune_real_scores, thres)
  EER = 100*((far+frr)/2) #In this case far and frr are the same

  #HTER on the test set
  dev_far, dev_frr = bob.measure.farfrr(devel_attack_scores, devel_real_scores, thres)
  test_far, test_frr = bob.measure.farfrr(test_attack_scores, test_real_scores, thres)
  HTER_dev = 100* ((dev_far+dev_frr)/2)
  HTER_test = 100* ((test_far+test_frr)/2)

  print("EER in the " + args.dev_set + " database: %.2f%%" % (EER) )
  print("")
  print("HTER in dev set in the " + args.test_set + " database: %.2f%%" % (HTER_dev))
  print("HTER in test set in the " + args.test_set + " database: %.2f%%" % (HTER_test))
  print("")
 
  return 0


if __name__ == "__main__":
  main()
