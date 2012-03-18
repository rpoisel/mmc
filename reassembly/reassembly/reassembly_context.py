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


class CReassembly(object):

    def __init__(self, *args, **kwargs):
        super(CReassembly, self).__init__(*args, **kwargs)

    def assemble(self, pOptions, pFragments, pCaller):
        # sort list so that header fragments are at the beginning
        pFragments.sort(key=lambda lFrag: lFrag.mIsHeader, reverse=True)
        lIdxNoHeader = 0
        for lFrag in pFragments:
            if lFrag.mIsHeader == True:
                lIdxNoHeader += 1
        self._assemble_impl(pOptions, pFragments, lIdxNoHeader, pCaller)

    # interface only
    def _assemble_impl(self, pOptions, pSortedFrags, lIdxNoHeader, pCaller):
        pass


class CReassemblyPUP(CReassembly):

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUP, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        # the place to invoke _reassemblePUP
        self._reassemblePUP(pSortedFrags, pIdxNoHeader, pOptions,
                self._compareFrags)

    def _compareFrags(self, pFragment1, pFragment2, pSimilarity):
        # comparison function for two fragments
        return -1

    def _reassemblePUP(self, pSortedFrags, pIdxNoHeader, pOptions, pCmp):
        lNumFrg = len(pSortedFrags) - pIdxNoHeader
        lPaths = [lCnt for lCnt in xrange(pIdxNoHeader)]
        while lNumFrg > 0:
            lBestResult = {'idxHead': -1, 'idxFrag': -1, 'idxHdr': -1, \
                    'cmp': 0}
            for lIdxHdr in xrange(pIdxNoHeader):
                lIdxHead = lPaths[lIdxHdr]
                for lIdxFrag in xrange(pIdxNoHeader, len(pSortedFrags)):
                    if pSortedFrags[lIdxFrag].mNextIdx == -1 and \
                            lIdxHead != lIdxFrag:
                        lCmp = pCmp(pSortedFrags[lIdxHead], \
                                pSortedFrags[lIdxFrag], \
                                pOptions.similarity)
                        if lCmp > lBestResult['cmp']:
                            lBestResult = {'idxHead': lIdxHead, \
                                    'idxFrag': lIdxFrag, 'idxHdr': lIdxHdr, \
                                    'cmp': lCmp}
            # check for ambiguous result
            if lBestResult['cmp'] == 0:
                break
            pSortedFrags[lBestResult['idxHead']].mNextIdx = \
                    lBestResult['idxFrag']
            lPaths[lBestResult['idxHdr']] = lBestResult['idxFrag']
            lNumFrg -= 1


class CReassemblyPUPVideo(CReassemblyPUP):

    FRG_HDR = 0
    FRG_BEGIN = 1
    FRG_END = 2
    FRG_SMALL = 3

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUPVideo, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
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
                self.__decodeVideo(lFragHeader.mOffset + lFragHeader.mSize - \
                        pOptions.extractsize, pOptions.output,
                        "hdr", lCntHdr, lFragHeader.mSize, lHdrData,
                        CReassemblyPUPVideo.FRG_HDR,
                        lRecoverFH)
            else:
                self.__decodeVideo(lFragHeader.mOffset + pOptions.hdrsize,
                        pOptions.output, "hdr", lCntHdr, lFragHeader.mSize,
                        lHdrData, CReassemblyPUPVideo.FRG_HDR, lRecoverFH)
                lFragHeader.mIsSmall = True
            self.__determineCut(pOptions.output, "hdr", lFragHeader, lCntHdr,
                    pOptions.minpicsize)

            # extract fragments frames
            # TODO check if fragment has already been decoded successfully
            lCntFrg = 0
            for lFrag in pSortedFrags[pIdxNoHeader:]:
                logging.info("Extracting fragment: " + str(lFrag))
                # extract begin
                lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                if lFrag.mSize > pOptions.extractsize:
                    self.__decodeVideo(lFrag.mOffset, pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CReassemblyPUPVideo.FRG_BEGIN, lRecoverFH)
                    # extract end
                    self.__decodeVideo(lFrag.mOffset + lFrag.mSize - \
                            pOptions.extractsize,
                            pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CReassemblyPUPVideo.FRG_END, lRecoverFH)
                else:
                    # extract the whole fragment at once
                    self.__decodeVideo(lFrag.mOffset, pOptions.output, "frg",
                            lCntFrg, lFrag.mSize, lHdrData,
                            CReassemblyPUPVideo.FRG_SMALL, lRecoverFH)
                    lFrag.mIsSmall = True
                self.__determineCut(pOptions.output, "frg", lFrag, lCntFrg,
                        pOptions.minpicsize)
                lCntFrg += 1

            lCntHdr += 1
            pCaller.progressCallback(50 * \
                    lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))

        # remove those fragments which could not be decoded
        pSortedFrags = [lFrag for lFrag in pSortedFrags if \
                (lFrag.mIsHeader == True) or \
                (lFrag.mIsHeader == False and lFrag.mPicBegin != "" and \
                lFrag.mPicEnd != "")]

        # determine reconstruction paths
        self._reassemblePUP(pSortedFrags,
                pIdxNoHeader,
                pOptions,
                self._compareVideoFrags)

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

    def _compareVideoFrags(self, pFragment1, pFragment2, pSimilarity):
        lImage1 = Image.open(pFragment1.mPicEnd, "r")
        lImage2 = Image.open(pFragment2.mPicBegin, "r")

        # size check
        if lImage1.size != lImage2.size or \
                lImage1.mode != 'RGB' or \
                lImage2.mode != 'RGB':
            return -1

        # histogram intersection
        lReturn = 0
        lHist1 = lImage1.histogram()
        lHist2 = lImage2.histogram()
        for lChannel in xrange(3):
            for lIntensity in xrange(256):
                lIdx = lChannel * 256 + lIntensity
                if abs(lHist1[lIdx] - lHist2[lIdx]) < pSimilarity:
                    lReturn += 1

        logging.info("Value for " + pFragment1.mPicEnd + " <=> " + \
                pFragment2.mPicBegin + ": " + str(lReturn))

        return lReturn

    def __determineCut(self, pOut, pDir, pFrag, pIdx, pMinPicSize):
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

        lFiles.sort(key=lambda lFile: lFile[0])

        lRefSize = max(lFiles, key=lambda lFile: lFile[1])[1]
        lFiles.reverse()
        for lFile in lFiles:
            if lFile[1] > (lRefSize * pMinPicSize / 100):
                pFrag.mPicEnd = lFile[0]
                lFiles.remove(lFile)
                break
        if pFrag.mIsHeader == False:
            for lFile in lFiles:
                if lFile[1] > (lRefSize * pMinPicSize / 100):
                    pFrag.mPicBegin = lFile[0]
                    lFiles.remove(lFile)
                    break

        for lFile in lFiles:
            os.remove(lFile[0])

    def __decodeVideo(self, pOffset, pOut, pDir, pIdx, pLen,
            pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        lFilename = pOut + os.sep + pDir + os.sep
        if pWhence == CReassemblyPUPVideo.FRG_HDR:
            lFilename += "h"
        elif pWhence == CReassemblyPUPVideo.FRG_BEGIN:
            lFilename += "b"
        elif pWhence == CReassemblyPUPVideo.FRG_SMALL:
            lFilename += "s"
        else:
            lFilename += "e"
        lFilename += "%04d" % (pIdx) + "%04d.png"
        lDecoder = decoder.CDecoder.getDecoder(lFilename)
        lDecoder.open(lFilename)
        lDecoder.write(pHdrData)
        lDecoder.write(pFH.read(pLen))
        lDecoder.close()


class CReassemblyPUPJpeg(CReassemblyPUP):

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUPJpeg, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        # the place to invoke _reassemblePUP
        self._reassemblePUP(pSortedFrags, pIdxNoHeader, pOptions,
                self._compareFrags)

    def _compareFrags(self, pFragment1, pFragment2, pSimilarity):
        # comparison function for two fragments
        return -1


class CReassemblyPerm(CReassembly):

    def __init__(self, *args, **kwargs):
        super(CReassemblyPerm, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        lCntHdr = 0
        logging.info("Trying combinations... ")
        for lFragHeader in pSortedFrags[0:pIdxNoHeader]:
            lDir = pOptions.output + os.sep + str(lCntHdr)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
            lRecoverFH = open(pOptions.imagefile, "rb")
            for lCnt in xrange(len(pSortedFrags[pIdxNoHeader:]) + 1):
                for lPermutation in \
                        itertools.permutations(pSortedFrags[pIdxNoHeader:], \
                        lCnt):
                    logging.info("Trying permutation: " + str(lFragHeader) + \
                            ' ' + \
                            ''.join([str(lFrag) + ' ' for lFrag in \
                            lPermutation]))
                    lDecoder = decoder.CDecoder.getDecoder(\
                            pOptions.outputformat \
                            )
                    lDecoder.open(lDir + os.sep + pOptions.outputformat)
                    lRecoverFH.seek(lFragHeader.mOffset, os.SEEK_SET)
                    lDecoder.write(lRecoverFH.read(lFragHeader.mSize))
                    for lFrag in lPermutation:
                        lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                        lDecoder.write(lRecoverFH.read(lFrag.mSize))
                    lDecoder.close()
            lRecoverFH.close()
            lCntHdr += 1
            pCaller.progressCallback(100 * lCntHdr / \
                    len(pSortedFrags[0:pIdxNoHeader]))
        logging.info("... Finished!")
        pCaller.progressCallback(100)


class CReassemblyFactory:

    sReassemblyMethodsVideo = {'Parallel Unique Path': CReassemblyPUPVideo, \
            'Permutations': CReassemblyPerm}

    sReassemblyMethodsJpeg = {}

    sReassemblyMethodsPng = {}

    @staticmethod
    def getAssemblyMethodsVideo():
        return sorted(CReassemblyFactory.sReassemblyMethodsVideo.keys())

    @staticmethod
    def getInstanceVideo(pWhich):
        return CReassemblyFactory.sReassemblyMethodsVideo[pWhich]()
