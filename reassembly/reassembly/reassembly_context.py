import os
import os.path
import logging
import itertools
import subprocess
import fnmatch
import shutil
import platform

import Image

import decoder

class CReassembly:

    FRG_HDR = 0
    FRG_BEGIN = 1
    FRG_END = 2
    FRG_SMALL = 3

    @staticmethod
    def assemble(pOptions, pFragments, pCaller):
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
            logging.info("Extracting header: " + str(lFragHeader))
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
                logging.info("Extracting fragment: " + str(lFrag))
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
            pCaller.progressCallback(50 * lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))

        # remove those fragments which could not be decoded
        pSortedFrags = [lFrag for lFrag in pSortedFrags if \
                (lFrag.mIsHeader == True) or \
                (lFrag.mIsHeader == False and lFrag.mPicBegin != "" and lFrag.mPicEnd != "")]

        # determine reconstruction paths
        CReassembly.reassemblePUP(pSortedFrags, 
                pIdxNoHeader, 
                pOptions, 
                CReassembly.compareVideoFrags)

        # extract determined videos
        lFH = None
        logging.info("8<=============== FRAGMENT PATHs ==============")
        for lIdxHdr in xrange(pIdxNoHeader):
            lDir = pOptions.output + os.sep + str(lIdxHdr)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
            lDecoder = decoder.CDecoder.getDecoder(pOptions.outputformat)
            lDecoder.open(lDir + os.sep + pOptions.outputformat)
            lFrag = pSortedFrags[lIdxHdr]
            while True:
                lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                lDecoder.write(lRecoverFH.read(lFrag.mSize))
                logging.info("Current Fragment: " + str(lFrag))
                if lFrag.mNextIdx == -1:
                    break
                lFrag = pSortedFrags[lFrag.mNextIdx]
            lDecoder.close()

        if lFH != None:
            lFH.close()
        logging.info("8<=============== FRAGMENT PATHs ==============")

        lRecoverFH.close()
        pCaller.progressCallback(100)

    @staticmethod
    def __diffFrames(pPath1, pPath2, pDiff):
        lImage1 = Image.open(pPath1, "r")
        lImage2 = Image.open(pPath2, "r")
        
        # size check
        if lImage1.size != lImage2.size or lImage1.mode != 'RGB' or lImage2.mode != 'RGB':
            return -1

        # histogram intersection
        lReturn = 0
        lHist1 = lImage1.histogram()
        lHist2 = lImage2.histogram()
        for lChannel in xrange(3):
            for lIntensity in xrange(256):
                lIdx = lChannel * 256 + lIntensity
                if abs(lHist1[lIdx] - lHist2[lIdx]) < pDiff:
                    lReturn += 1 

        logging.info("Value for " + pPath1 + " <=> " + pPath2 + ": " + str(lReturn))

        return lReturn

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
        lDecoder = decoder.CDecoder.getDecoder(lFilename)
        lDecoder.open(lFilename)
        lDecoder.write(pHdrData)
        lDecoder.write(pFH.read(pLen))
        lDecoder.close()

    @staticmethod
    def __assemble_permutations(pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        lCntHdr = 0
        logging.info("Trying combinations... ")
        for lFragHeader in pSortedFrags[0:pIdxNoHeader]:
            lDir = pOptions.output + os.sep + str(lCntHdr)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
            lRecoverFH = open(pOptions.imagefile, "rb")
            for lCnt in xrange(len(pSortedFrags[pIdxNoHeader:])+1):
                for lPermutation in itertools.permutations(pSortedFrags[pIdxNoHeader:], lCnt):
                    logging.info("Trying permutation: " + str(lFragHeader) + ' ' + \
                            ''.join([str(lFrag)+' ' for lFrag in lPermutation]))
                    lDecoder = decoder.CDecoder.getDecoder(pOptions.outputformat)
                    lDecoder.open(lDir + os.sep + pOptions.outputformat)
                    lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
                    lDecoder.write(lRecoverFH.read(lFragHeader.mSize))
                    for lFrag in lPermutation:
                        lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                        lDecoder.write(lRecoverFH.read(lFrag.mSize))
                    lDecoder.close()
            lRecoverFH.close()
            lCntHdr += 1
            pCaller.progressCallback(100 * lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))
        logging.info("... Finished!")
        pCaller.progressCallback(100)

    @staticmethod
    def getAssemblyMethods():
        return sorted(CReassembly.sReassemblyMethods.keys())


    @staticmethod
    def compareVideoFrags(pFragment1, pFragment2, pSimilarity):
        return CReassembly.__diffFrames(pFragment1.mPicEnd, \
                pFragment2.mPicBegin, \
                pSimilarity)
        
    @staticmethod
    def reassemblePUP(pSortedFrags, pIdxNoHeader, pOptions, pCmp):
        lNumFrg = len(pSortedFrags) - pIdxNoHeader
        lPaths = [lCnt for lCnt in xrange(pIdxNoHeader)]
        while lNumFrg > 0:
            lBestResult = {'idxHead':-1, 'idxFrag':-1, 'idxHdr':-1, 'cmp':0}
            for lIdxHdr in xrange(pIdxNoHeader):
                lIdxHead = lPaths[lIdxHdr]
                for lIdxFrag in xrange(pIdxNoHeader, len(pSortedFrags)):
                    if pSortedFrags[lIdxFrag].mNextIdx == -1 and lIdxHead != lIdxFrag:
                        lCmp = pCmp(pSortedFrags[lIdxHead], \
                                pSortedFrags[lIdxFrag], \
                                pOptions.similarity)
                        if lCmp > lBestResult['cmp']:
                            lBestResult = {'idxHead':lIdxHead, 'idxFrag':lIdxFrag, 'idxHdr':lIdxHdr, 'cmp':lCmp}
            # check for ambiguous result
            if lBestResult['cmp'] == 0:
                break
            pSortedFrags[lBestResult['idxHead']].mNextIdx = lBestResult['idxFrag']
            lPaths[lBestResult['idxHdr']] = lBestResult['idxFrag']
            lNumFrg -= 1

    sReassemblyMethods = {'image processor':{'name':'image processor', 'func':__assemble_imageproc}, \
            'permutations':{'name':'permutations', 'func':__assemble_permutations}}

    def __init__(self):
        pass
