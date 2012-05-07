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
        self.mFiles = []

    def assemble(self, pOptions, pFragments, pCaller):
        lIdxNoHeader = 0
        for lIdx in xrange(len(pFragments)):
            if pFragments[lIdx].mIsHeader == True:
                lIdxNoHeader += 1

        self._assemble_impl(pOptions, pFragments, lIdxNoHeader, pCaller)

    # interface only
    def _assemble_impl(self, pOptions, pSortedFrags, lIdxNoHeader, pCaller):
        pass

    def _extractReassembledFragments(self, pSortedFrags, pIdxNoHeader,
            pOptions, pInputFileType):
        # extract determined files
        lRecoverFH = open(pOptions.imagefile, "rb")
        logging.info("8<=============== FRAGMENT PATHs ==============")
        for lIdxHdr in xrange(pIdxNoHeader):
            lFrag = pSortedFrags[lIdxHdr]
            lFrag.mFilePath = pOptions.output + os.sep + str(lIdxHdr)
            if not os.path.exists(lFrag.mFilePath):
                os.makedirs(lFrag.mFilePath)
            lFrag.mFilePath = lFrag.mFilePath + os.sep + pOptions.outputformat

            lDecoder = decoder.CDecoder.getDecoder(pInputFileType,
                    pOptions.outputformat)
            lDecoder.open(lFrag.mFilePath)

            while True:
                lRecoverFH.seek(lFrag.mOffset, os.SEEK_SET)
                lDecoder.write(lRecoverFH.read(lFrag.mSize))
                logging.info("Current Fragment: " + str(lFrag))
                if lFrag.mNextIdx == -1:
                    break
                lFrag = pSortedFrags[lFrag.mNextIdx]
            lDecoder.close()
        if lRecoverFH != None:
            lRecoverFH.close()
        logging.info("8<=============== FRAGMENT PATHs ==============")
        return


class CReassemblyPUP(CReassembly):

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUP, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        # the place to invoke _reassemblePUP
        self._reassemblePUP(pSortedFrags, pIdxNoHeader, pOptions,
                self._compareFrags)

    def _compareFrags(self, pPath, pFragment, pSimilarity):
        # compares pFragment with the Fragments stored in pPath
        return -1

    def _reassemblePUP(self, pSortedFrags, pIdxNoHeader, pOptions, pCmp):
        lNumFrg = len(pSortedFrags) - pIdxNoHeader
        lReassemblyPaths = [lCnt for lCnt in xrange(pIdxNoHeader)]
        # TODO check number of non-header frags
        lRemainingFrags = [lCnt for lCnt in xrange(pIdxNoHeader,
            lNumFrg + pIdxNoHeader)]

        for lHdr in xrange(pIdxNoHeader):
            lReassemblyPaths[lHdr] = [pSortedFrags[lHdr]]

        #As long as there are Fragments
        while len(lRemainingFrags) > 0:
            lBestResult = {'idxHdr': -1, 'idxFrag': -1, 'result': 0}
            #Iterate all Header Fragments
            for lIdxHdr in xrange(pIdxNoHeader):
                #Iterate all non-Header Fragments
                for lIdxFrag in lRemainingFrags:
                    lResult = pCmp(lReassemblyPaths[lIdxHdr], \
                              pSortedFrags[lIdxFrag], \
                              pOptions.similarity)
                    if lResult > lBestResult['result']:
                        lBestResult = {'idxHdr': lIdxHdr, \
                                    'idxFrag': lIdxFrag, \
                                    'result': lResult}
            # check for ambiguous result
            if lBestResult['result'] == 0:
                break
            pSortedFrags[lBestResult['idxHdr']].mNextIdx = \
                    lBestResult['idxFrag']
            lReassemblyPaths[lBestResult['idxHdr']].\
                    append(pSortedFrags[lBestResult['idxFrag']])
            lRemainingFrags.remove(lBestResult['idxFrag'])


class CReassemblyPUPVideo(CReassemblyPUP):

    FRG_HDR = 0
    FRG_BEGIN = 1
    FRG_END = 2
    FRG_SMALL = 3

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUPVideo, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):
        for lDir in [os.path.join(pOptions.output, "hdr"),
                os.path.join(pOptions.output, "frg")]:
            if os.path.exists(lDir):
                shutil.rmtree(lDir)
            if not os.path.exists(lDir):
                os.makedirs(lDir)

        lRecoverFH = open(pOptions.imagefile, "rb")

        # extract headers frames
        lCntHdr = 0
        for lFragHeaderIdx in xrange(0, pIdxNoHeader):
            logging.info("Extracting header: " + \
                    str(pSortedFrags[lFragHeaderIdx]))
            lRecoverFH.seek(pSortedFrags[lFragHeaderIdx].mOffset, os.SEEK_SET)
            lHdrData = lRecoverFH.read(pOptions.hdrsize)
            if pSortedFrags[lFragHeaderIdx].mSize > pOptions.extractsize:
                self.__decodeVideo(pSortedFrags[lFragHeaderIdx].mOffset + \
                        pSortedFrags[lFragHeaderIdx].mSize - \
                        pOptions.extractsize, pOptions.output,
                        "hdr", lCntHdr, pSortedFrags[lFragHeaderIdx].mSize,
                        lHdrData,
                        CReassemblyPUPVideo.FRG_HDR,
                        lRecoverFH)
            else:
                self.__decodeVideo(pSortedFrags[lFragHeaderIdx].mOffset + \
                        pOptions.hdrsize,
                        pOptions.output, "hdr", lCntHdr,
                        pSortedFrags[lFragHeaderIdx].mSize,
                        lHdrData, CReassemblyPUPVideo.FRG_HDR, lRecoverFH)
                pSortedFrags[lFragHeaderIdx].mIsSmall = True
            self.__determineCut(pOptions.output, "hdr",
                    pSortedFrags[lFragHeaderIdx], lCntHdr,
                    pOptions.minpicsize)

            # extract fragments frames
            # TODO check if fragment has already been decoded successfully
            lCntFrg = 0
            for lFragIdx in xrange(pIdxNoHeader, len(pSortedFrags)):
                logging.info("Extracting fragment: " + \
                        str(pSortedFrags[lFragIdx]))
                # extract begin
                lRecoverFH.seek(pSortedFrags[lFragIdx].mOffset, os.SEEK_SET)
                if pSortedFrags[lFragIdx].mSize > pOptions.extractsize:
                    self.__decodeVideo(pSortedFrags[lFragIdx].mOffset,
                            pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CReassemblyPUPVideo.FRG_BEGIN, lRecoverFH)
                    # extract end
                    self.__decodeVideo(pSortedFrags[lFragIdx].mOffset + \
                            pSortedFrags[lFragIdx].mSize - \
                            pOptions.extractsize,
                            pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CReassemblyPUPVideo.FRG_END, lRecoverFH)
                else:
                    # extract the whole fragment at once
                    self.__decodeVideo(pSortedFrags[lFragIdx].mOffset,
                            pOptions.output, "frg",
                            lCntFrg, pSortedFrags[lFragIdx].mSize, lHdrData,
                            CReassemblyPUPVideo.FRG_SMALL, lRecoverFH)
                    pSortedFrags[lFragIdx].mIsSmall = True
                self.__determineCut(pOptions.output, "frg",
                        pSortedFrags[lFragIdx], lCntFrg,
                        pOptions.minpicsize)
                lCntFrg += 1

            lCntHdr += 1
            pCaller.progressCallback(50 * \
                    lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))

        # remove those fragments which could not be decoded
        # TODO check if del() is an alternative to creating a new array
        pSortedFrags = [lFrag for lFrag in pSortedFrags if \
                (lFrag.mIsHeader == True and lFrag.mPicEnd != "") or \
                (lFrag.mIsHeader == False and lFrag.mPicBegin != "" and \
                lFrag.mPicEnd != "")]

        lIdxNoHeader = -1
        for lIdx in xrange(len(pSortedFrags)):
            if pSortedFrags[lIdx].mIsHeader == False:
                lIdxNoHeader = lIdx
                break

        # determine reconstruction paths
        self._reassemblePUP(pSortedFrags,
                lIdxNoHeader,
                pOptions,
                self._compareVideoFrags)

        # extract determined videos
        self._extractReassembledFragments(pSortedFrags,
                lIdxNoHeader, pOptions, "h264")
        pCaller.progressCallback(100)

    def _compareVideoFrags(self, pPath, pFragment2, pSimilarity):
        pFragment1 = pPath[len(pPath) - 1]
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
        for lFile in os.listdir(os.path.join(pOut, pDir)):
            if fnmatch.fnmatch(lFile, "b%04d*.png" % pIdx) or \
                    fnmatch.fnmatch(lFile, "[he]%04d*.png" % pIdx) or \
                    fnmatch.fnmatch(lFile, "s%04d*.png" % pIdx):
                lFilename = os.path.join(pOut, pDir, lFile)
                lFiles.append((lFilename, os.path.getsize(lFilename)))

        # determine begin and end frames
        if len(lFiles) < 1:
            return

        lSortedFiles = sorted(lFiles, key=lambda lFile: lFile[0])

        lRefSize = max(lSortedFiles, key=lambda lFile: lFile[1])[1]
        for lFile in reversed(lSortedFiles):
            if lFile[1] > (lRefSize * pMinPicSize / 100):
                pFrag.mPicEnd = lFile[0]
                lSortedFiles.remove(lFile)
                break
        if pFrag.mIsHeader == False:
            for lFile in lSortedFiles:
                if lFile[1] > (lRefSize * pMinPicSize / 100):
                    pFrag.mPicBegin = lFile[0]
                    lSortedFiles.remove(lFile)
                    break

        for lFile in lSortedFiles:
            os.remove(lFile[0])

    def __decodeVideo(self, pOffset, pOut, pDir, pIdx, pLen,
            pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        lFilename = os.path.join(pOut, pDir) + os.sep
        if pWhence == CReassemblyPUPVideo.FRG_HDR:
            lFilename += "h"
        elif pWhence == CReassemblyPUPVideo.FRG_BEGIN:
            lFilename += "b"
        elif pWhence == CReassemblyPUPVideo.FRG_SMALL:
            lFilename += "s"
        else:
            lFilename += "e"
        lFilename += "%04d" % (pIdx) + "%04d.png"
        lDecoder = decoder.CDecoder.getDecoder("h264", lFilename)
        lDecoder.open(lFilename)
        lDecoder.write(pHdrData)
        lDecoder.write(pFH.read(pLen))
        lDecoder.close()


class CReassemblyPUPJpeg(CReassemblyPUP):

    def __init__(self, *args, **kwargs):
        super(CReassemblyPUPJpeg, self).__init__(*args, **kwargs)

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader, pCaller):

        for lDir in [pOptions.output + "/hdr", pOptions.output + "/frg",
                pOptions.output + "/path"]:
            if os.path.exists(lDir):
                shutil.rmtree(lDir)
            if not os.path.exists(lDir):
                os.makedirs(lDir)

        lRecoverFH = open(pOptions.imagefile, "rb")

        # extract headers frames
        for lFragHeaderIdx in xrange(0, pIdxNoHeader):
            logging.info("Extracting header: " + str(lFragHeaderIdx))

            #Creating reassembly File Objects
            lFile = CFileJpeg(lFragHeaderIdx)
            lFile.mFileType = "JPEG"
            lFile.mFileName = "h%d" % (lFragHeaderIdx)
            self.mFiles.append(lFile)

            lFragment = pSortedFrags[lFragHeaderIdx]
            lRecoverFH.seek(lFragment.mOffset, os.SEEK_SET)
            lData = lRecoverFH.read(lFragment.mSize)
            lPath = os.path.join(pOptions.output, "hdr") + os.sep
            self.__analyzeJpeg(lFile, lData)

            #Write RAW Data
            lFilename = lPath + lFragment.mName + ".raw"
            lFragment.mRawDataPath = lFilename
            lFile = open(lFilename, "wb")
            lFile.write(lData)
            lFile.close()

            #Convert to PNG
            lFilename = lPath + lFragment.mName + ".png"
            lFragment.mPicBegin = lFilename
            lDecoder = decoder.CDecoder.getDecoder("jpg", lFilename)
            lDecoder.open(lFilename)
            lDecoder.write(lData)
            lDecoder.write("\xFF\xD9")
            lDecoder.close()

        # extract non-header fragments
        for lFragHeaderIdx in xrange[pIdxNoHeader, len(pSortedFrags)]:
            lFragment = pSortedFrags[lFragHeaderIdx]
            logging.info("Extracting fragments: " + str(lFragment))
            lRecoverFH.seek(lFragment.mOffset, os.SEEK_SET)
            lData = lRecoverFH.read(lFragment.mSize)

            lPath = os.path.join(pOptions.output, "frg") + os.sep
            lName = "f%d" % (lFragHeaderIdx)
            lFragment.mName = lName

            #Write RAW Data (No Header and no EOI Marker)
            lFilename = lPath + lFragment.mName + ".raw"
            lFragment.mRawDataPath = lFilename
            lFile = open(lFilename, "wb")
            lFile.write(lData)
            lFile.close()

        lRecoverFH.close()
        #pCaller.progressCallback(50 * \
        #        lCntHdr / len(pSortedFrags[0:pIdxNoHeader]))
        pCaller.progressCallback(50)

        # the place to invoke _reassemblePUP
        self._reassemblePUP(pSortedFrags, pIdxNoHeader, pOptions,
                self._compareFrags)

        self._extractReassembledFragments(pSortedFrags,
                pIdxNoHeader, pOptions, "jpg")

        pCaller.progressCallback(100)

    def _compareFrags(self, pPath, pFragment, pSimilarity):

        #The first Fragment in the Path must be an Header
        if not pPath[0].mIsHeader:
            return -1

        #The Header doesn't need any more fragments
        if pPath[0].mComplete:
            return 0

        # Path image which is deleted if path changes.
        # this makes it more performant
        lPathImage = "/tmp/temp/path/"
        for lFragment in pPath:
            lPathImage += lFragment.mName

        #Assemble the current reassemblypath with the fragment
        lReassemblyImage = lPathImage.replace("/tmp/temp/path",
                "/tmp/temp/frg")
        lReassemblyImage += pFragment.mName + ".jpg"
        lPathImage += ".jpg"

        #Write the ReassemblyPathImage (All fragments up to now)
        #if not os.path.exists(lPathImage):
        pPath[0].mReassemblyPathSize = 0
        lFile = open(lPathImage, "wb")
        for lFrag in pPath:
            lRead = open(lFrag.mRawDataPath, "rb")
            lFile.write(lRead.read(lFrag.mSize))
            pPath[0].mReassemblyPathSize += lFrag.mSize
            lRead.close()
        lFile.close()

        #Reassemble the Base Path with the new fragment
        lBaseFragments = open(lPathImage, "rb")
        lFragment = open(pFragment.mRawDataPath, "rb")
        lReassembly = open(lReassemblyImage, "wb")
        lReassembly.write(lBaseFragments.read(pPath[0].mReassemblyPathSize))
        lReassembly.write(lFragment.read(pFragment.mSize))
        lReassembly.write("\xFF\xD9")
        lReassembly.close()
        lBaseFragments.close()

        lFile = open(lPathImage, "ab")
        lFile.write("\xFF\xD9")
        lFile.close()

        ###### Analysis of the Image #####

        # Open the base fragment image and the full image (base + compare)
        lBaseFragmentImage = Image.open(lPathImage)
        lCompareFragmentImage = Image.open(lReassemblyImage)

        # Determine the end of the base fragment image and the compare image
        lBaseFragmentCut = self.__determineJpegCut(lBaseFragmentImage)
        lCompareFragmentCut = self.__determineJpegCut(lCompareFragmentImage)

        #Check the size of the new fragment. If it is less than a line
        #in the picture, we have to reduce the histogram samples

        #Determine the last line of each part
        WIDTH = 0
        HEIGHT = 1
        X = 0
        Y = 1
        #height of a line sampled by jpeg, usually 16px
        lLineHeight = (lBaseFragmentCut[1][Y] - lBaseFragmentCut[0][Y]) + 1
        #Difference between the both image cuts
        lLineDiff = [lCompareFragmentCut[0][X] - lBaseFragmentCut[0][X],
                     lCompareFragmentCut[0][Y] - lBaseFragmentCut[0][Y]]
        lBaseFragmentLine = [None, None]
        lCompareFragmentLine = [None, None]

        #Todo: Review the calculation process
        #lCompareFragmentCut is in the same line as lBaseFragmentCut
        if lLineDiff[Y] <= lLineHeight:
            #same line, only need to calculate one line
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lCompareFragmentCut[0][X] - 1,
                                     lCompareFragmentCut[1][Y]]
            lCompareFragmentLine[1] = None
        elif lLineDiff[X] < 0:
            #two lines but second line is long enough
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lBaseFragmentImage.size[WIDTH] - 1,
                                     lCompareFragmentCut[0][Y] - 1]
            lCompareFragmentLine[1] = [0,
                                     lCompareFragmentCut[0][Y],
                                     lCompareFragmentCut[0][X] - 1,
                                     lCompareFragmentCut[1][Y]]
        else:
            #there is enough data
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lBaseFragmentImage.size[WIDTH] - 1,
                                     lCompareFragmentCut[0][Y] - 1]
            lCompareFragmentLine[1] = [0,
                                     lCompareFragmentCut[0][Y],
                                     lCompareFragmentCut[0][X] - 1,
                                     lBaseFragmentCut[1][Y] + lLineHeight]

        #Get the lines of the Base Fragment
        lBaseFragmentLine[0] = [lCompareFragmentLine[0][0],
                              lCompareFragmentLine[0][1] - lLineHeight,
                              lCompareFragmentLine[0][2],
                              lCompareFragmentLine[0][3] - lLineHeight]
        if lCompareFragmentLine[1] != None:
            lBaseFragmentLine[1] = [lCompareFragmentLine[1][0],
                                  lCompareFragmentLine[1][1] - lLineHeight,
                                  lCompareFragmentLine[1][2],
                                  lCompareFragmentLine[1][3] - lLineHeight]
        else:
            lCompareFragmentLine[1] = [0, 0, 0, 0]
            lBaseFragmentLine[1] = [0, 0, 0, 0]
            # lBaseFragmentLine[0] = [lBaseFragmentCut[0][X],
            #   lBaseFragmentCut[0][Y]-(lLineHeight-1),
            #   lBaseFragmentImage.size[WIDTH]-1,
            #   lBaseFragmentCut[0][Y]-1]
            # lBaseFragmentLine[1] = [0,
            #   lBaseFragmentCut[0][Y],
            #   lBaseFragmentCut[0][X]-1,
            #   lBaseFragmentCut[1][Y]]

        #According to the Header, enough image data is already in place
        if lBaseFragmentCut[1][X] >= lBaseFragmentImage.size[WIDTH] \
                and lBaseFragmentCut[1][Y] >= lBaseFragmentImage.size[HEIGHT]:
            pPath[0].mComplete = True
            return 0

        #Histogram of the base fragments last data line
        lHist1 = lBaseFragmentImage.crop(lBaseFragmentLine[0]).histogram() + \
                BaseFragmentImage.crop(lBaseFragmentLine[1]).histogram()

        #Histogram of the compare fragments last data line
        lHist2 = lCompareFragmentImage.crop(lCompareFragmentLine[0]).\
                histogram() + \
                lCompareFragmentImage.crop(lCompareFragmentLine[1]).histogram()

        #Do the Histogram intersection
        lWeight = 0
        for lIdx in xrange(len(lHist1)):
            if abs(lHist1[lIdx] - lHist2[lIdx]) < pSimilarity:
                lWeight += 1

        logging.info("Value for " + pPath[0].mName + " <=> " + \
                pFragment.mName + ": " + str(lWeight))

        return lWeight

    def __determineJpegCut(self, pImage):

        X = 0
        Y = 1

        #Convert to Grey Values to determine the border better
        lImage = pImage.convert("L")
        PictureEnd = [[-1, -1], [-1, -1]]
        for y in reversed(range(0, pImage.size[Y])):
            #Also look at the neighbors to prevent correct grey pixels
            if not lImage.getpixel((lImage.size[X] - 1, y)) == 128 or \
               not lImage.getpixel((lImage.size[X] - 3, y)) == 128 or \
               not lImage.getpixel((lImage.size[X] - 5, y)) == 128:
                    PictureEnd[0][Y] = y + 1
                    break

        #There is no cut in the Image
        if(PictureEnd[0][Y] == lImage.size[Y]):
            return [[lImage.size[X], lImage.size[Y] - 15], lImage.size]

        for x in reversed(range(0, lImage.size[X])):
            #Also look at the neighbors to prevent correct grey pixels
            if not lImage.getpixel((x, PictureEnd[0][Y])) == 128 or \
               not lImage.getpixel((x, PictureEnd[0][Y] + 2)) == 128 or \
               not lImage.getpixel((x, PictureEnd[0][Y] + 4)) == 128:
                PictureEnd[0][X] = x + 1
                break

        PictureEnd[1][X] = PictureEnd[0][X]
        PictureEnd[1][Y] = PictureEnd[0][Y] + 15  # 2*8-1

        return PictureEnd

    #Analyzes the JPEG Fragment for Markers
    def __analyzeJpeg(self, pFile, pData):
        for i in range(len(pData)):
        #Not the last Byte
            if i < len(pData) - 1:
                #We have found a Marker
                if ord(pData[i]) == 0xFF:
                    b2 = ord(pData[i + 1])
                    if b2 == CFileJpeg.MRK_SOS:
                        pFile.mMarker[CFileJpeg.MRK_SOS] = i
                    elif b2 == CFileJpeg.MRK_SOI:
                        pFile.mMarker[CFileJpeg.MRK_SOI] = i

        #Calculate the Scan Header Length. It is positioned right after the
        #SOS marker and is part of the image section (scan section) it contains
        #additional information about the image.
        #Ls is the Length of the "Scan Header Length" of two bytes size
        Ls = ord(pData[(pFile.mMarker[CFileJpeg.MRK_SOS] + 2)]) * 255 + \
                ord(pData[(pFile.mMarker[CFileJpeg.MRK_SOS] + 3)])
        pFile.mDataBegin = pFile.mMarker[CFileJpeg.MRK_SOS] + Ls + 2
        pFile.mHeaderData = pData[:pFile.mDataBegin]

    def __writeJpeg(self, pOffset, pOut, pDir, pIdx, pLen,
            pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        lFilename = os.path.join(pOut, pDir) + os.sep
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


class CReassemblyFactory:

    sReassemblyMethodsVideo = {'Parallel Unique Path': CReassemblyPUPVideo}

    sReassemblyMethodsJpeg = {'Parallel Unique Path': CReassemblyPUPJpeg}

    sReassemblyMethodsPng = {}

    #Video
    @staticmethod
    def getAssemblyMethodsVideo():
        return sorted(CReassemblyFactory.sReassemblyMethodsVideo.keys())

    @staticmethod
    def getInstanceVideo(pWhich):
        return CReassemblyFactory.sReassemblyMethodsVideo[pWhich]()

    #JPEG
    @staticmethod
    def getAssemblyMethodsJpeg():
        return sorted(CReassemblyFactory.sReassemblyMethodsJpeg.keys())

    @staticmethod
    def getInstanceJpeg(pWhich):
        return CReassemblyFactory.\
                sReassemblyMethodsJpeg[pWhich]()

    #PNG
    @staticmethod
    def getAssemblyMethodsPng():
        return sorted(CReassemblyFactory.sReassemblyMethodsPng.keys())

    @staticmethod
    def getInstancePng(pWhich):
        return CReassemblyFactory.sReassemblyMethodsPng[pWhich]()

class CFile(object):

    def __init__(self, pFragmentId):
        self.mFileName = "",pFragmentId
        self.mFragmentId = pFragmentId
        self.mDataBegin = -1
        self.mComplete = False
        self.mFragments = []
        #TODO
        self.mFragments.append(pFragmentId)

    def getLastFragment(self):
        self.mFragments[len(self.mFragments)-1]

    def __str__(self):
        return "H(%s)" % self.mFragmentId

class CFileJpeg(CFile):
    
    MRK_SOS = 0xDA
    MRK_SOI = 0xD8
    MRK_EOI = 0xD9
    
    def __init__(self,pBlockSize):
        super(CFile, self).__init__()

        self.mFileType = "JPEG"
        #All Markers have a relative Position
        self.mMarker = [-1] * 255
        self.mCut = (-1, -1)
        self.mRawDataPath = ""
        self.mReassemblyPathSize = 0  #TODO: What is that?
        self.mDataBegin = None
        self.mHeaderData = None


    def __str__(self):
        lString = super(CFile, self).__str__()
        lString += " (JPEG)"
        return lString
    
class CFileH264(CFile):
    
    def __init__(self,pBlockSize):
        super(CFile, self).__init__()
        self.mPicBegin = ""
        self.mPicEnd = ""
    
    def __str__(self):
        lString = super(CFile, self).__str__()
        lString += " (H264)"
        return lString
