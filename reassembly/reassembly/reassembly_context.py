import os
import itertools
import subprocess

class CReassembly:

    FRG_HDR = 0
    FRG_BEGIN = 1
    FRG_END = 2
    FRG_SMALL = 3

    @staticmethod
    def assemble(pOptions, pFragments, pValidator, pCaller):
        # sort list so that header fragments are at the beginning
        lSortedFrags = sorted(pFragments, key=lambda lFrag: lFrag.mIsHeader, reverse = True)
        lIdxNoHeader = 0
        for lFrag in lSortedFrags:
            if lFrag.mIsHeader == False:
                break
            lIdxNoHeader += 1

        CReassembly.sReassemblyMethods[pOptions.assemblymethod]['func'].__get__(None, CReassembly)(pOptions, lSortedFrags, lIdxNoHeader, pCaller)

    @staticmethod
    def __assemble_imageproc(pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        for lDir in [pOptions.output + "/hdr", pOptions.output + "/frg"]:
            if not os.path.exists(lDir):
                os.makedirs(lDir)

        lRecoverFH = open(pOptions.imagefile, "rb")

        # extract headers frames
        lCntHdr = 0
        for lFragHeader in pSortedFrags[0:pIdxNoHeader]:
            print("Processing header: " + str(lFragHeader))
            lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
            lHdrData = lRecoverFH.read(pOptions.hdrsize)
            if lFragHeader.mSize > pOptions.extractsize:
                CReassembly.__decodeVideo(lFragHeader.mOffset + lFragHeader.mSize - \
                        pOptions.extractsize, pOptions.output,
                        "hdr", lCntHdr, lFragHeader.mSize, lHdrData, CReassembly.FRG_HDR,
                        lRecoverFH)
            else:
                CReassembly.__decodeVideo(lFragHeader.mOffset + pOptions.hdrsize,
                        pOptions.output, "hdr", lCntHdr, lFragHeader.mSize, lHdrData,
                        CReassembly.FRG_HDR, lRecoverFH)

            # extract fragments frames
            lCntFrg = 0
            for lFrag in pSortedFrags[pIdxNoHeader:]:
                print("Processing fragment: " + str(lFrag))
                # extract begin
                lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                if lFrag.mSize > pOptions.extractsize:
                    CReassembly.__decodeVideo(lFrag.mOffset, pOptions.output, "frg", 
                            lCntFrg, pOptions.extractsize, lHdrData, CReassembly.FRG_BEGIN,
                            lRecoverFH)
                    # extract end
                    CReassembly.__decodeVideo(lFrag.mOffset + lFrag.mSize - \
                            pOptions.extractsize,
                            pOptions.output, "frg", 
                            lCntFrg, pOptions.extractsize, lHdrData, CReassembly.FRG_END,
                            lRecoverFH)
                else:
                    # extract the whole fragment at once
                    CReassembly.__decodeVideo(lFrag.mOffset, pOptions.output, "frg", 
                            lCntFrg, lFrag.mSize, lHdrData, CReassembly.FRG_SMALL,
                            lRecoverFH)
                lCntFrg += 1
            
            print("Finished header processing: " + str(lFragHeader))
            lCntHdr += 1
            pCaller.progressCallback(100 * lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))

        # check for similarities

        lRecoverFH.close()
        pCaller.progressCallback(100)

    @staticmethod
    def __decodeVideo(pOffset, pOut, pDir, pIdx, pLen, pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        if pWhence == CReassembly.FRG_HDR:
            lFilename = "h%04d" % (pIdx) + "%04d.png"
        elif pWhence == CReassembly.FRG_BEGIN:
            lFilename = "b%04d" % (pIdx) + "%04d.png"
        elif pWhence == CReassembly.FRG_SMALL:
            lFilename = "s%04d" % (pIdx) + "%04d.png"
        else:
            lFilename = "e%04d" % (pIdx) + "%04d.png"
        lFFMpeg = subprocess.Popen(
                ["ffmpeg", "-y", "-i", "-", pOut + \
                        "/" + pDir + "/" + lFilename],
                bufsize = 512, stdin = subprocess.PIPE)
        lFFMpeg.stdin.write(pHdrData)
        lFFMpeg.stdin.write(pFH.read(pLen))
        lFFMpeg.stdin.flush()

    @staticmethod
    def __assemble_permutations(pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        lCntHdr = 0
        print("Trying combinations... ")
        for lFragHeader in pSortedFrags[0:pIdxNoHeader]:
            lDir = pOptions.output + "/" + str(lCntHdr)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
            lRecoverFH = open(pOptions.imagefile, "rb")
            for lCnt in xrange(len(pSortedFrags[pIdxNoHeader:])+1):
                try:
                    for lPermutation in itertools.permutations(pSortedFrags[pIdxNoHeader:], lCnt):
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
            pCaller.progressCallback(100 * lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))
        print("... Finished!")
        pCaller.progressCallback(100)

    @staticmethod
    def getAssemblyMethods():
        return CReassembly.sReassemblyMethods.keys()

    sReassemblyMethods = {'permutations':{'name':'permutations', 'func':__assemble_permutations},\
            'image processor':{'name':'image processor', 'func':__assemble_imageproc}}

    def __init__(self):
        pass
