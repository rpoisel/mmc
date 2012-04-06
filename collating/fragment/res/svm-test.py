#!/usr/bin/env python

import os
import sys

import svmutil

sys.path.append("..")

from fragment_context import FileType


def read_ranges(pPathRange):
    lReturn = {}
    lFH = open(pPathRange, "r")
    for lLine in lFH:
        lValues = lLine.split()
        if len(lValues) == 3:
            lReturn[int(lValues[0])] = (int(lValues[1]), int(lValues[2]))
    lFH.close()
    return lReturn


def scale_values(pBFD, pLower, pUpper, pRanges):
    for lKey in pBFD.keys():
        if pBFD[lKey] == pRanges[lKey][0]:
            pBFD[lKey] = pLower
        elif pBFD[lKey] == pRanges[lKey][1]:
            pBFD[lKey] = pUpper
        else:
            pBFD[lKey] = pLower + (pUpper - pLower) * \
                    (pBFD[lKey] - pRanges[lKey][0]) / \
                    (pRanges[lKey][1] - pRanges[lKey][0])


def main():
    try:
        lModel = svmutil.svm_load_model(sys.argv[1])
        lRanges = read_ranges(sys.argv[2])
        lFile = sys.argv[3]
        lBlockSize = int(sys.argv[4])
    except IndexError, pExc:
        print "Usage: " + sys.argv[0] + " <model-file> <range-file> "\
                "<problem-file> <block-size>"
        sys.exit(-1)

    if lFile.lower().endswith(".jpg"):
        lFileType = FileType.FT_JPG
    elif lFile.lower().endswith(".png"):
        lFileType = FileType.FT_PNG
    elif lFile.lower().endswith(".h264"):
        lFileType = FileType.FT_H264
    elif lFile.lower().endswith(".mp3"):
        lFileType = FileType.FT_MP3
    elif lFile.lower().endswith(".pdf"):
        lFileType = FileType.FT_PDF
    else:
        lFileType = FileType.FT_UNKNOWN

    lFH = open(lFile, "rb")
    while True:
        lBlock = lFH.read(lBlockSize)
        if lBlock == '':
            break
        lBFD = {}
        for lCnt in xrange(len(lBlock)):
            lByteVal = ord(lBlock[lCnt]) + 1
            if lByteVal not in lBFD:
                lBFD[lByteVal] = 0
            lBFD[lByteVal] += 1
        scale_values(lBFD, -1., 1., lRanges)
        #print lBFD
        lPredict = svmutil.svm_predict([lFileType], [lBFD], lModel)[0]
        print lPredict

    lFH.close()


if __name__ == "__main__":
    main()
