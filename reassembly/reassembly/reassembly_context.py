import os
import itertools
import subprocess

class CReassembly:
    def __init__(self):
        pass

    def assemble(self, pOptions, pFragments, pValidator, pCaller):
        # sort list so that header fragments are at the beginning
        lSortedFrags = sorted(pFragments, key=lambda lFrag: lFrag.mIsHeader, reverse = True)
        lIdxNoHeader = 0
        for lFrag in lSortedFrags:
            if lFrag.mIsHeader == False:
                break
            lIdxNoHeader += 1

        lCntHdr = 0

        print("Trying combinations... ")
        for lFragHeader in lSortedFrags[0:lIdxNoHeader]:
            lDir = pOptions.output + "/" + str(lCntHdr)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
            lRecoverData = ""
            lFFMpeg = subprocess.Popen(
                    ["ffmpeg", "-i", "-", lDir + "/" + pOptions.outputformat], 
                    bufsize=512, stdin=subprocess.PIPE) #, stderr=subprocess.PIPE)
            lRecoverFH = open(pOptions.imagefile, "rb")
            lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
            lRecoverData += lRecoverFH.read(lFragHeader.mSize)
            for lCnt in xrange(len(lSortedFrags[lIdxNoHeader:])+1):
                for lPermutation in itertools.permutations(lSortedFrags[lIdxNoHeader:], lCnt):
                    for lFrag in lPermutation:
                        lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                        lRecoverData += lRecoverFH.read(lFrag.mSize)
            lFFMpeg.communicate(input=lRecoverData)
            lRecoverFH.close()
            lCntHdr += 1
            pCaller.progressCallback(100 * len(lSortedFrags[0:lIdxNoHeader]) / (lCntHdr))
        pCaller.progressCallback(100)
