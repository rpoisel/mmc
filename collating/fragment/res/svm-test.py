#!/usr/bin/env python

import os
import sys

import svmutil

def main():
    try:
        lModel = svmutil.svm_load_model(sys.argv[1])
        lY, lX = svmutil.svm_read_problem(sys.argv[2])
        print svmutil.svm_predict(lY, lX, lModel)[0]
    except IndexError, pExc:
        print "Usage: " + sys.argv[0] + " <model-file> <problem-file>"

if __name__ == "__main__":
    main()
