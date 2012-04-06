#!/usr/bin/env python

import os
import sys

import svmutil

import copy

def scale_values(pX, pLower, pUpper):
    # TODO: WRONG, scale to range file which contains the 
    #       min/max values of features

    # do this for the first feature only
    for lDict in pX:
        print "Dict: " + str(lDict)
        lMin = lDict[min(lDict, key=lambda x : lDict[x])]
        print "Min: " + str(lMin)
        lMax = lDict[max(lDict, key=lambda x : lDict[x])]
        print "Max: " + str(lMax)
        for lKey in lDict.keys():
            if lDict[lKey] == lMin:
                lDict[lKey] = pLower
            elif lDict[lKey] == lMax:
                lDict[lKey] = pUpper
            else:
                lDict[lKey] = pLower + (pUpper - pLower) * (lDict[lKey] - lMin) / (lMax - lMin)

    # scale according to values from ranges file


def main():
    try:
        lModel = svmutil.svm_load_model(sys.argv[1])
        print lModel
        lY, lX = svmutil.svm_read_problem(sys.argv[2])
        scale_values(lX, -1., 1.)
        #lX = normalize_instances(lX)
        print svmutil.svm_predict(lY, lX, lModel)[0]
        #print lX
    except IndexError, pExc:
        print "Usage: " + sys.argv[0] + " <model-file> <problem-file>"

if __name__ == "__main__":
    main()
