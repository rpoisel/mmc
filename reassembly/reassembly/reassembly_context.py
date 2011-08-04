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
            lRecoverFH = open(pOptions.imagefile, "rb")
            for lCnt in xrange(len(lSortedFrags[lIdxNoHeader:])+1):
                try:
                    for lPermutation in itertools.permutations(lSortedFrags[lIdxNoHeader:], lCnt):
                        print("Trying permutation: " + str(lFragHeader) + ' ' + \
                                ''.join([str(lFrag)+' ' for lFrag in lPermutation]))
                        lFFMpeg = subprocess.Popen(
                                ["ffmpeg", "-y", "-i", "-", lDir + "/" + pOptions.outputformat], 
                                bufsize = 512, stdin = subprocess.PIPE)
                        lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
                        lFFMpeg.stdin.write(lRecoverFH.read(lFragHeader.mSize))
                        for lFrag in lPermutation:
                            lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                            lFFMpeg.stdin.write(lRecoverFH.read(lFrag.mSize))
                        lFFMpeg.stdin.flush()
                except IOError:
                    # TODO return error
                    pass
            lRecoverFH.close()
            lCntHdr += 1
            pCaller.progressCallback(100 * len(lSortedFrags[0:lIdxNoHeader]) / (lCntHdr))
        print("... Finished!")
        pCaller.progressCallback(100)
