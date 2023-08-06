#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Feb  8 09:10:01 CET 2013

"""
Compute

The first directory is the base for
"""

import argparse
import bob
import numpy
import os, sys


#from ..helpers import score_fusion_reader
from antispoofing.utils.db import *
from antispoofing.fusion.readers import *
from antispoofing.fusion.score_fusion.score_fusion import *

from antispoofing.crossdatabase.helpers import *

def main():

    available_dbs = get_db_names()

    basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    INPUT_DIR = os.path.join(basedir, 'scores')
    available_dbs = get_db_names()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', nargs='+', default=INPUT_DIR, help='Base directory containing the scores (defaults to "%(default)s")')

    parser.add_argument('-a', '--average', action='store_true', dest='average', default=False, help='Average a file of scores (Video based approach)')

    parser.add_argument('-i', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')

    parser.add_argument('-d', '--databases', dest='dbs', nargs='+', type=str, choices=available_dbs, help='Development set databases.')

    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

    Database.create_parser(parser, implements_any_of='video')

    args = parser.parse_args()

    inputDir     = args.scoresDir
    average      = args.average
    average_size = args.average_size
    dbs          = args.dbs


    if(len(inputDir) < 2):
        raise ValueError("Is necessary at least 2 path of scores")

    #Loading the database
    database = args.cls(args)

    ########################
    #Querying the database
    ########################
    #trainRealObjects, trainAttackObjects = database.get_train_data()

    #loading each object from devset
    #develRealScores   = []
    #develAttackScores = []

    thresholds = []
    for i in  range(len(dbs)):

        db = get_db_by_name(dbs[i])
        develRealObjects, develAttackObjects = db.get_devel_data()

        #Loading the scores
        dR = ScoreReader(develRealObjects,inputDir[i]).getScores(average=average, average_size=average_size)
        dA = ScoreReader(develAttackObjects,inputDir[i]).getScores(average=average, average_size=average_size)

        #develRealScores.append(dR)
        #develAttackScores.append(dA)

        #Defining the threshold
        thresholds.append(bob.measure.eer_threshold(dA,dR))

    testRealObjects, testAttackObjects   = database.get_test_data()
    testRealScores   = ScoreFusionReader(testRealObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)
    testAttackScores   = ScoreFusionReader(testAttackObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)

    testScores = numpy.concatenate((testRealScores,testAttackScores),axis=0)
    decisions = numpy.zeros(shape=testScores.shape)


    for i in  range(len(dbs)):
        decisions[:,i] = testScores[:,i] > thresholds[i]

    Q = ScoreFusion.QAverage(decisions)

    print("Countermeasure trained with the " + str(database) + " database.")
    print("Q-Statistic: %.2f" % Q)



    return 0

if __name__ == "__main__":
    main()