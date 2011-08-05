import os
import os.path
import itertools
import subprocess
import fnmatch
import shutil

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
            if lFrag.mIsHeader == True:
                lIdxNoHeader += 1
            lFrag.mIsSmall = False
            lFrag.mPicBegin = ""
            lFrag.mPicEnd = ""

        CReassembly.sReassemblyMethods[pOptions.assemblymethod]['func'].__get__(None, CReassembly)(pOptions, lSortedFrags, lIdxNoHeader, pCaller)

    @staticmethod
    def __assemble_imageproc(pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        for lDir in [pOptions.output + "/hdr", pOptions.output + "/frg"]:
            if os.path.exists(lDir):
                shutil.rmtree(lDir)
            if not os.path.exists(lDir):
                os.makedirs(lDir)

        lRecoverFH = open(pOptions.imagefile, "rb")

        # extract headers frames
        lCntHdr = 0
        for lFragHeader in pSortedFrags[0:pIdxNoHeader]:
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
                lFragHeader.mIsSmall = True
            CReassembly.__determineCut(pOptions.output, "hdr", lFragHeader, lCntHdr, pOptions.minpicsize)

            # extract fragments frames
            # TODO check if fragment has already been decoded successfully
            lCntFrg = 0
            for lFrag in pSortedFrags[pIdxNoHeader:]:
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
                    lFrag.mIsSmall = True
                CReassembly.__determineCut(pOptions.output, "frg", lFrag, lCntFrg, pOptions.minpicsize)
                lCntFrg += 1
            
            lCntHdr += 1
            pCaller.progressCallback(100 * lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))

        # check for similarities
        print("8<=============== FRAGS ==============")
        for lFrag in pSortedFrags:
            print lFrag
        print("8<=============== FRAGS ==============")

        # extract determined videos

        lRecoverFH.close()
        pCaller.progressCallback(100)

    @staticmethod
    def __determineCut(pOut, pDir, pFrag, pIdx, pMinPicSize):
        # determine relevant files
        lFiles = []
        for lFile in os.listdir(pOut + os.sep + pDir):
            if fnmatch.fnmatch(lFile, "b%04d*.png" % pIdx) or \
                    fnmatch.fnmatch(lFile, "[he]%04d*.png" % pIdx) or \
                    fnmatch.fnmatch(lFile, "s%04d*.png" % pIdx):
                lFilename = pOut + os.sep + pDir + os.sep + lFile
                lFiles.append((lFilename, os.path.getsize(lFilename)))

        # determine begin and end frames
        if len(lFiles) < 1:
            return

        lSortedFiles = sorted(lFiles, key=lambda lFile: lFile[0])

        lRefSize = max(lSortedFiles, key = lambda lFile:lFile[1])[1]
        for lFile in reversed(lSortedFiles):
            if lFile[1] > (lRefSize * pMinPicSize/100):
                pFrag.mPicEnd = lFile[0]
                lSortedFiles.remove(lFile)
                break
        if pFrag.mIsHeader == False:
            for lFile in lSortedFiles:
                if lFile[1] > (lRefSize * pMinPicSize/100):
                    pFrag.mPicBegin = lFile[0]
                    lSortedFiles.remove(lFile)
                    break

        for lFile in lSortedFiles:
            os.remove(lFile[0])

    @staticmethod
    def __decodeVideo(pOffset, pOut, pDir, pIdx, pLen, 
            pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        lFilename = pOut + os.sep + pDir + os.sep
        if pWhence == CReassembly.FRG_HDR:
            lFilename += "h"
        elif pWhence == CReassembly.FRG_BEGIN:
            lFilename += "b"
        elif pWhence == CReassembly.FRG_SMALL:
            lFilename += "s"
        else:
            lFilename += "e"
        lFilename += "%04d" % (pIdx) + "%04d.png"
        lFFMpeg = subprocess.Popen(
                ["ffmpeg", "-y", "-i", "-", lFilename],
                bufsize = 512, stdin = subprocess.PIPE,
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        lFFMpeg.stdin.write(pHdrData)
        lFFMpeg.stdin.write(pFH.read(pLen))
        lFFMpeg.communicate()

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
                                ["ffmpeg", "-y", "-i", "-", lDir + os.sep + pOptions.outputformat], 
                                bufsize = 512, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                        lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
                        lFFMpeg.stdin.write(lRecoverFH.read(lFragHeader.mSize))
                        for lFrag in lPermutation:
                            lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                            lFFMpeg.stdin.write(lRecoverFH.read(lFrag.mSize))
                        lFFMpeg.communicate()
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
