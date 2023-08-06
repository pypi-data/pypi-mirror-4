#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Feb  8 09:10:01 CET 2013

"""
Compute
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


def computeQStatistic(scores, thres):

    decisions = scores > thres
    Q = ScoreFusion.QAverage(decisions)

    return Q



def main():

    basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    INPUT_DIR = os.path.join(basedir, 'scores')
    available_dbs = get_db_names()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', nargs='+', default=INPUT_DIR, help='Base directory containing the scores (defaults to "%(default)s")')

    #parser.add_argument('-o', '--output-dir', type=str, dest='outputDir', default='', help='Base directory that will be used to save the fused scores.')

    parser.add_argument('-a', '--average', action='store_true', dest='average', default=False, help='Avege a file of scores (Video based approach)')

    parser.add_argument('-i', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')

    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

    parser.add_argument('-d', '--dev-set', type=str, dest='dev_set', default=available_dbs[0], choices=available_dbs, help='The database used in the devel set')

    parser.add_argument('-t', '--test-set', type=str, dest='test_set', default=available_dbs[0], choices=available_dbs, help='The database used in the test set')


    ScoreFusion.create_parser(parser)


    args = parser.parse_args()

    inputDir     = args.scoresDir
    average      = args.average
    average_size = args.average_size

    if(len(inputDir) < 2):
        raise ValueError("Is necessary at least 2 path of scores")

    #Loading databases
    devDB  = get_db_by_name(args.dev_set)
    testDB = get_db_by_name(args.test_set)

    ########################
    #Querying the database
    ########################
    trainRealObjects, trainAttackObjects = devDB.get_train_data()
    develRealObjects, develAttackObjects = devDB.get_devel_data()
    testRealObjects, testAttackObjects   = testDB.get_test_data()

    #Loading the scores
    trainRealScores   = ScoreFusionReader(trainRealObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)
    trainAttackScores   = ScoreFusionReader(trainAttackObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)

    develRealScores   = ScoreFusionReader(develRealObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)
    develAttackScores = ScoreFusionReader(develAttackObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)

    testRealScores   = ScoreFusionReader(testRealObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)
    testAttackScores   = ScoreFusionReader(testAttackObjects,inputDir).getConcatenetedScores(average=average, average_size=average_size)

    data_to_normalization = numpy.concatenate((trainRealScores,trainAttackScores),axis=0)
    fusion = ScoreFusion.load(args,data_to_normalization)
    fusion.train([trainRealScores,trainAttackScores])

    #trainRealFusedScores = fusion(trainRealScores);trainAttackFusedScores = fusion(trainAttackScores);

    develRealFusedScores = fusion(develRealScores);develAttackFusedScores = fusion(develAttackScores);

    testRealFusedScores = fusion(testRealScores);testAttackFusedScores = fusion(testAttackScores);

    if numpy.mean(develRealFusedScores) < numpy.mean(develAttackFusedScores):
        #trainRealFusedScores = trainRealFusedScores * -1; trainAttackFusedScores = trainAttackFusedScores * -1
        develRealFusedScores = develRealFusedScores * -1; develAttackFusedScores = develAttackFusedScores * -1
        testRealFusedScores = testRealFusedScores * -1; testAttackFusedScores = testAttackFusedScores * -1


    #Result analysis
    thres = bob.measure.eer_threshold(develAttackFusedScores, develRealFusedScores)

    #FAR, FRR = bob.measure.farfrr(trainAttackFusedScores, trainRealFusedScores, thres)
    #HTER_train = (FAR+FRR)/2.

    FAR, FRR = bob.measure.farfrr(develAttackFusedScores, develRealFusedScores, thres)
    HTER_dev = ((FAR+FRR)/2.) * 100

    FAR, FRR = bob.measure.farfrr(testAttackFusedScores, testRealFusedScores, thres)
    HTER_test = ((FAR+FRR)/2.) * 100

    print("Tests reported in the: " + args.test_set)
    print 'Score fusion using:',fusion, 'with', fusion.normalizer, ':'
    #print("HTER - train: " + str(HTER_train))
    print("HTER - devel: %.2f%% " % HTER_dev)
    print("HTER - test: %.2f%%" % HTER_test)

    return 0

if __name__ == "__main__":
    main()