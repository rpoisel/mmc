#!/usr/bin/env python

import sys
import os
import zlib

sys.path.append("..")

from fragment_context import FileType


def main():
    try:
        lBlockSize = int(sys.argv[2])
        lPath = sys.argv[1]
        for lRoot, lDirs, lFiles in os.walk(lPath):
            for lFile in lFiles:
                with open(os.path.join(lRoot, lFile), "rb") as lFH:
                    # continue over the first block
                    lFH.seek(lBlockSize, os.SEEK_SET)
                    lBlock = lFH.read(lBlockSize)
                    while lBlock != "" and len(lBlock) == lBlockSize:
                        # calculate Kolmogorov complexity
                        lCompr = zlib.compress(lBlock)
                        lComplexity = len(lCompr)
                        # calc BFD
                        lBFD = [0 for lCnt in xrange(256)]
                        for lCnt in xrange(lBlockSize):
                            lBFD[ord(lBlock[lCnt])] += 1

                        if lFile.lower().endswith(".jpg"):
                            lFeatureStr = str(FileType.FT_JPG)
                        elif lFile.lower().endswith(".png"):
                            lFeatureStr = str(FileType.FT_PNG)
                        elif lFile.lower().endswith(".h264"):
                            lFeatureStr = str(FileType.FT_H264)
                        elif lFile.lower().endswith(".mp3"):
                            lFeatureStr = str(FileType.FT_MP3)
                        elif lFile.lower().endswith(".pdf"):
                            lFeatureStr = str(FileType.FT_PDF)
                        elif lFile.lower().endswith(".zip"):
                            lFeatureStr = str(FileType.FT_ZIP)
                        elif lFile.lower().endswith(".rar"):
                            lFeatureStr = str(FileType.FT_RAR)
                        elif lFile.lower().endswith(".doc"):
                            lFeatureStr = str(FileType.FT_DOC)
                        elif lFile.lower().endswith(".xls"):
                            lFeatureStr = str(FileType.FT_XLS)
                        else:
                            break
                        for lCnt in xrange(256):
                            lFeatureStr += " " + str(lCnt + 1) + ":" + \
                                    str(lBFD[lCnt])
                        # add Kolmogorov complexity
                        #lFeatureStr += " 256:" + str(lComplexity)
                        print lFeatureStr
                        lBlock = lFH.read(lBlockSize)
    except IndexError, pExc:
        print "Usage: " + sys.argv[0] + " <path> <block-size>"
        sys.exit(-1)
    except IOError, pExc:
        print "Error: " + str(pExc)

if __name__ == "__main__":
    main()
