import os.path
import logging
import fnmatch
import shutil
import Image
import decoder


class CReassembly(object):

    def __init__(self, pFileHandler):
        self.mFiles = []
        self.mFileHandler = pFileHandler
        logging.info("CReassembly constructor finished")

    def assemble(self, pOptions, pFragments, pCaller):
        lIdxNoHeader = 0
        for lIdx in xrange(len(pFragments)):
            if pFragments[lIdx].mIsHeader == 1:
                lIdxNoHeader += 1

        self.mFiles = self.mFileHandler.prepareFiles(pOptions,
                                                      pFragments,
                                                      lIdxNoHeader)
        pCaller.progressCallback(50)
        self._assemble_impl(pOptions, pFragments, lIdxNoHeader)
        self._extractReassembledFragments(pFragments, pOptions, "jpg")
        pCaller.progressCallback(100)
        return self.mFiles

    # interface only
    def _assemble_impl(self, pOptions, pSortedFrags, lIdxNoHeader):
        pass

    def _extractReassembledFragments(self, pSortedFrags,
            pOptions, pInputFileType):
        # extract determined files
        logging.info("Beginning extraction of reassembled files")
        for lFile in self.mFiles:
            lFile.mFilePath = pOptions.output + os.sep + \
                                str(lFile.getHeaderFragmentId())
            if not os.path.exists(lFile.mFilePath):
                os.makedirs(lFile.mFilePath)
            lFile.mFilePath = lFile.mFilePath + os.sep + pOptions.outputformat

            lDecoder = decoder.CDecoder.getDecoder(pOptions.outputformat)
            lDecoder.open(lFile.mFilePath)

            logging.debug("Extract File " + lFile.mFileName + ": " +
                          str(lFile.mFragments))

            for lFragIdx in lFile.mFragments:
                lFrag = pSortedFrags[lFragIdx]
                lData = self.mFileHandler.readFragment(lFrag, pOptions)
                lDecoder.write(lData)

            lDecoder.close()
        logging.info("Extraction finished")
        return


class CReassemblyPUP(CReassembly):

    def __init__(self, pFileHandler):
        super(CReassemblyPUP, self).__init__(pFileHandler)
        logging.info("CReassemblyPUP constructor finished")

    def _assemble_impl(self, pOptions, pSortedFrags, pIdxNoHeader):
        lIdxNoHeader = 0
        for lIdx in xrange(len(pSortedFrags)):
            if pSortedFrags[lIdx].mIsHeader == 1:
                lIdxNoHeader += 1
        lNumFrg = len(pSortedFrags) - pIdxNoHeader

        lRemainingFrags = [lCnt for lCnt in xrange(pIdxNoHeader,
            lNumFrg + pIdxNoHeader)]

        #As long as there are Fragments
        while len(lRemainingFrags) > 0:
            lBestResult = {'idxPath': -1, 'idxFrag': -1, 'result': 0}
            #Iterate all Header Fragments
            for lPathId in xrange(len(self.mFiles)):
                #Only look at remaining paths
                if self.mFiles[lPathId].mComplete is True:
                    continue
                #Iterate all non-Header Fragments
                for lIdxFrag in lRemainingFrags:
                    #Fragment has an error
                    if pSortedFrags[lIdxFrag].mSize == 0:
                        continue

                    lResult = self.mFileHandler.compareFrags(pSortedFrags,
                              self.mFiles[lPathId],
                              lIdxFrag,
                              pOptions)
                    logging.debug("Comparing Path" +
                                 str(self.mFiles[lPathId].mFragments) +
                                 " <=> f(" + str(lIdxFrag) + "): " +
                                 str(lResult))
                    if lResult > lBestResult['result']:
                        lBestResult = {'idxPath': lPathId,
                                    'idxFrag': lIdxFrag,
                                    'result': lResult}

            # check for ambiguous result
            if lBestResult['result'] == 0:
                break

            self.mFiles[lBestResult['idxPath']].\
                    addFragmentId(lBestResult['idxFrag'])
            if pSortedFrags[lBestResult['idxFrag']].mIsFooter == 1:
                self.mFiles[lBestResult['idxPath']].mComplete = True
                logging.debug("Path " +
                              str(self.mFiles[lBestResult['idxPath']].
                              mFragments) + " is complete")
            lRemainingFrags.remove(lBestResult['idxFrag'])


class CAbstractFileTypeHandler(object):
    def prepareFiles(self, pOptions, pSortedFrags, pIdxNoHeader):
        pass

    def compareFrags(self, pFragments, pPath, pFragmentId, pOptions):
        pass

    def readFragment(self, pFragment, pOptions):
        lRecoverFH = open(pOptions.imagefile, "rb")
        lRecoverFH.seek(pFragment.mOffset, os.SEEK_SET)
        lData = lRecoverFH.read(pFragment.mSize)
        lRecoverFH.close()
        return lData


class CVideoHandler(CAbstractFileTypeHandler):

    FRG_HDR = 0
    FRG_BEGIN = 1
    FRG_END = 2
    FRG_SMALL = 3

    PATTERN_PATH = "08d"

    def __init__(self):
        logging.info("CVideoFileHandler constructor finished")

    def prepareFiles(self, pOptions, pSortedFrags, pIdxNoHeader):
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
            logging.debug("Extracting header: " +
                    str(pSortedFrags[lFragHeaderIdx]))

            lRecoverFH.seek(pSortedFrags[lFragHeaderIdx].mOffset, os.SEEK_SET)
            lHdrData = lRecoverFH.read(pOptions.hdrsize)
            if pSortedFrags[lFragHeaderIdx].mSize > pOptions.extractsize:
                self._decodeVideo(
                        pSortedFrags[lFragHeaderIdx].mOffset +
                            pSortedFrags[lFragHeaderIdx].mSize -
                            pOptions.extractsize,
                        pOptions.output,
                        "hdr",
                        lCntHdr,
                        pOptions.extractsize,
                        lHdrData,
                        CVideoHandler.FRG_HDR,
                        lRecoverFH)
            else:
                self._decodeVideo(pSortedFrags[
                    lFragHeaderIdx].mOffset + pOptions.hdrsize,
                    pOptions.output,
                    "hdr",
                    lCntHdr,
                    pSortedFrags[lFragHeaderIdx].mSize,
                    lHdrData,
                    CVideoHandler.FRG_HDR,
                    lRecoverFH)
                pSortedFrags[lFragHeaderIdx].mIsSmall = True
            self._determineCut(pOptions.output, "hdr",
                    pSortedFrags[lFragHeaderIdx], lCntHdr,
                    pOptions.minpicsize)

            # extract fragments frames
            # TODO check if fragment has already been decoded successfully

            lCntFrg = 0
            for lFragIdx in xrange(pIdxNoHeader, len(pSortedFrags)):
                logging.debug("Extracting fragment: " +
                        str(pSortedFrags[lFragIdx]))
                # extract begin
                lRecoverFH.seek(pSortedFrags[lFragIdx].mOffset, os.SEEK_SET)
                if pSortedFrags[lFragIdx].mSize > pOptions.extractsize:
                    self._decodeVideo(pSortedFrags[lFragIdx].mOffset,
                            pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CVideoHandler.FRG_BEGIN, lRecoverFH)
                    # extract end
                    self._decodeVideo(pSortedFrags[lFragIdx].mOffset +
                            pSortedFrags[lFragIdx].mSize -
                            pOptions.extractsize,
                            pOptions.output, "frg",
                            lCntFrg, pOptions.extractsize, lHdrData,
                            CVideoHandler.FRG_END, lRecoverFH)
                else:
                    # extract the whole fragment at once
                    self._decodeVideo(pSortedFrags[lFragIdx].mOffset,
                            pOptions.output, "frg",
                            lCntFrg, pSortedFrags[lFragIdx].mSize, lHdrData,
                            CVideoHandler.FRG_SMALL, lRecoverFH)
                    pSortedFrags[lFragIdx].mIsSmall = True
                self._determineCut(pOptions.output, "frg",
                        pSortedFrags[lFragIdx], lCntFrg,
                        pOptions.minpicsize)
                lCntFrg += 1

            lCntHdr += 1

        #Debugging purposes
        for lIdx in xrange(len(pSortedFrags)):
            logging.debug("Fragment " + str(lIdx) + ": mPicBegin: " +
                          pSortedFrags[lIdx].mPicBegin + " mPicEnd: " +
                          pSortedFrags[lIdx].mPicEnd)

        # remove those fragments which could not be decoded
        # TODO check if del() is an alternative to creating a new array
        # answer: http://stackoverflow.com/questions/1207406/\
        #             remove-items-from-a-list-while-iterating-in-python
        lFiles = []
        for lFragIdx in xrange(len(pSortedFrags)):
            lFrag = pSortedFrags[lFragIdx]
            if lFrag.mIsHeader == 1 and lFrag.mPicEnd != "":
                #Creating reassembly File Objects
                lFile = CFileVideo(lFragIdx)
                lFile.mFileType = "Video"
                lFile.mFileName = ("h%" +
                        CVideoHandler.PATTERN_PATH) % (lFragIdx)
                lFiles.append(lFile)
            elif (lFrag.mIsHeader == 0 and
                  (lFrag.mPicBegin == "" or lFrag.mPicEnd == "")):
                lFrag.mSize = 0
                logging.debug("Fragment " + str(lFragIdx) +
                        " does not contain beginning or ending frame")

        return lFiles

    def compareFrags(self, pFragments, pPath, pFragmentId, pOptions):
        lFragment1 = pFragments[pPath.getLastFragmentId()]
        lFragment2 = pFragments[pFragmentId]
        lImage1 = Image.open(lFragment1.mPicEnd, "r")
        lImage2 = Image.open(lFragment2.mPicBegin, "r")

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
                if abs(lHist1[lIdx] - lHist2[lIdx]) < pOptions.similarity:
                    lReturn += 1

        logging.debug("Value for " + lFragment1.mPicEnd + " <=> " +
                lFragment2.mPicBegin + ": " + str(lReturn))

        return lReturn

    def _determineCut(self, pOut, pDir, pFrag, pIdx, pMinPicSize):
        # determine relevant files
        lFiles = []
        for lFile in os.listdir(os.path.join(pOut, pDir)):
            if fnmatch.fnmatch(lFile, ("b%" +
                    CVideoHandler.PATTERN_PATH + "*.png") % pIdx) or \
                    fnmatch.fnmatch(lFile, ("[he]%" +
                    CVideoHandler.PATTERN_PATH + "*.png") % pIdx) or \
                    fnmatch.fnmatch(lFile, ("s%" +
                    CVideoHandler.PATTERN_PATH + "*.png") % pIdx):
                lFilename = os.path.join(pOut, pDir, lFile)
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
        if pFrag.mIsHeader == 0:
            for lFile in lFiles:
                if lFile[1] > (lRefSize * pMinPicSize / 100):
                    pFrag.mPicBegin = lFile[0]
                    lFiles.remove(lFile)
                    break

    def _decodeVideo(self, pOffset, pOut, pDir, pIdx, pLen,
            pHdrData, pWhence, pFH):
        pFH.seek(pOffset, os.SEEK_SET)
        lFilename = os.path.join(pOut, pDir) + os.sep
        if pWhence == CVideoHandler.FRG_HDR:
            lFilename += "h"
        elif pWhence == CVideoHandler.FRG_BEGIN:
            lFilename += "b"
        elif pWhence == CVideoHandler.FRG_SMALL:
            lFilename += "s"
        else:
            lFilename += "e"
        lFilename += ("%" + CVideoHandler.PATTERN_PATH) % (pIdx)
        lDecoder = decoder.CDecoder.getDecoder("video")  # , lFilename)
        lDecoder.open(lFilename + "%04d.png", lFilename + ".dat")
        lDecoder.write(pHdrData)
        lDecoder.write(pFH.read(pLen))
        lDecoder.close()
        # TODO determine cut right here and assign picture paths to
        #      the fragment


class CJpegHandler(CAbstractFileTypeHandler):

    def __init__(self):
        logging.info("CJpegFileHandler constructor finished")

    def prepareFiles(self, pOptions, pSortedFrags, pIdxNoHeader):

        lFiles = []
        for lDir in [pOptions.output + "/hdr", pOptions.output + "/frg",
                pOptions.output + "/path"]:
            if os.path.exists(lDir):
                shutil.rmtree(lDir)
            if not os.path.exists(lDir):
                os.makedirs(lDir)
        # extract headers frames
        for lFragHeaderIdx in xrange(0, pIdxNoHeader):

            #Creating reassembly File Objects
            lFile = CFileJpeg(lFragHeaderIdx)
            lFile.mFileType = "JPEG"
            lFile.mFileName = "h%d" % (lFragHeaderIdx)
            lFiles.append(lFile)

            lFragment = pSortedFrags[lFragHeaderIdx]
            lData = self.readFragment(lFragment, pOptions)
            lPath = os.path.join(pOptions.output, "hdr") + os.sep
            self._analyzeJpeg(lFile, lData)

            #Convert to PNG: Important for the Preview
            lFilename = lPath + lFile.mFileName + ".png"
            lFragment.mPicBegin = lFilename
            lDecoder = decoder.CDecoder.getDecoder("jpg", lFilename)
            lDecoder.open(lFilename)
            lDecoder.write(lData)
            lDecoder.write("\xFF\xD9")
            lDecoder.close()

        #Identify Footer fragments
        for lFragIdx in xrange(pIdxNoHeader, len(pSortedFrags)):
            lFragment = pSortedFrags[lFragIdx]
            lData = self.readFragment(lFragment, pOptions)
            if lData.__contains__("\xFF\xD9"):
                lFragment.mIsFooter = 1
            else:
                lFragment.mIsFooter = 0

        return lFiles

    def compareFrags(self, pFragments, pPath, pFragmentId, pOptions):
        #Terms:
        #(Reassembly)Path: All fragments up to the fragmentation point. This
        #                  Includes the header fragment and other frags.
        #CompareFragment: Fragment which gets compared to the Path
        #ReassemblyImage:  ReassemblyPath + CompareFragment
        #The Header doesn't need any more fragments
        if pPath.mComplete:
            logging.info("Fragment already complete")
            return 0
        logging.info("start compare")
        # Write all reassembled fragments in the reassembly path to the
        # disk. This includes the header fragment and reassembled fragments
        if pPath.mBaseImagePath is None:
            pPath.mBaseImagePath = os.path.join(pOptions.output, "path") + \
                                   os.sep
            pPath.mBaseImagePath += pPath.mFileName + ".jpg"
            lFile = open(pPath.mBaseImagePath, "wb")
            for lFragId in pPath.mFragments:
                lFile.write(self.readFragment(pFragments[lFragId], pOptions))
            lFile.write("\xFF\xD9")
            lFile.close()

        #Reassemble the Base Path with the new fragment
        lCompareImagePath = os.path.join(pOptions.output, "frg") + os.sep
        lCompareImagePath += str(pPath.mFragments) + "f" + str(pFragmentId) + \
                             ".jpg"
        lBaseImage = open(pPath.mBaseImagePath, "rb")
        lCompareImage = open(lCompareImagePath, "wb")

        lFragmentData = self.readFragment(pFragments[pFragmentId], pOptions)
        #Remove the tailing EOI marker (0xFFD9)
        lCompareImage.write(lBaseImage.read()[:-2])
        lCompareImage.write(lFragmentData)
        lCompareImage.write("\xFF\xD9")
        lCompareImage.close()
        lBaseImage.close()

        ###### Analysis of the Image #####

        # Open the base fragment image and the full image (base + compare)
        logging.info(pPath.mBaseImagePath)
        try:
            lCompareFragmentImage = Image.open(lCompareImagePath)
        except IOError:
            logging.error("Can't decode" + lCompareImagePath)
            return 0
        try:
            lBaseFragmentImage = Image.open(pPath.mBaseImagePath)
        except IOError:
            #TODO: This can be used as object validator
            logging.error("!!! Can't decode" + pPath.mBaseImagePath +
                    ". Assembled image could be decoded, "
                    "It is very probably the best match!")
            return 250

        # Determine the end of the base fragment image and the compare image
        if pPath.mVerticalSamplingSize is None:
            lBaseFragmentCut = self._determineJpegCut(lBaseFragmentImage)
            pPath.mVerticalSamplingSize = lBaseFragmentCut[1][1] - \
                                               lBaseFragmentCut[0][1] + 1
        else:
            lBaseFragmentCut = self._determineJpegCut(
                    lBaseFragmentImage,
                    pPath.mVerticalSamplingSize)
        lCompareFragmentCut = self._determineJpegCut(
                lCompareFragmentImage,
                pPath.mVerticalSamplingSize)

        #Check the size of the new fragment. If it is less than a line
        #in the picture, we have to reduce the histogram samples

        #Determine the last line of each part
        WIDTH = 0
        HEIGHT = 1
        X = 0
        Y = 1
        #height of a line sampled by jpeg, usually 16px
        lLineHeight = pPath.mVerticalSamplingSize
        #Difference between the both image cuts
        lLineDiff = [lCompareFragmentCut[0][X] - lBaseFragmentCut[0][X],
                     lCompareFragmentCut[0][Y] - lBaseFragmentCut[0][Y]]
        lBaseFragmentLine = [None, None]
        lCompareFragmentLine = [None, None]

        #Todo: Review the calculation process
        #lCompareFragmentCut is in the same line as lBaseFragmentCut
        if lLineDiff[Y] < lLineHeight:
            #same line, only need to calculate one line
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lCompareFragmentCut[0][X] - 1,
                                     lCompareFragmentCut[1][Y]]
            logging.debug("One Line, little data")
            lCompareFragmentLine[1] = None
        elif lLineDiff[X] < 0 and lLineDiff[Y] < 2 * lLineHeight:
            #two lines but second line is not long enough
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lBaseFragmentImage.size[WIDTH] - 1,
                                     lBaseFragmentCut[1][Y]]
            lCompareFragmentLine[1] = [0,
                                     lCompareFragmentCut[0][Y],
                                     lCompareFragmentCut[0][X] - 1,
                                     lCompareFragmentCut[1][Y]]
            logging.debug("Two lines, little data, lLineDiff=" +
                          str(lLineDiff))
        else:
            #there is enough data
            lCompareFragmentLine[0] = [lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[0][Y],
                                     lBaseFragmentImage.size[WIDTH] - 1,
                                     lBaseFragmentCut[1][Y]]
            lCompareFragmentLine[1] = [0,
                                     lBaseFragmentCut[0][Y] + lLineHeight,
                                     lBaseFragmentCut[0][X],
                                     lBaseFragmentCut[1][Y] + lLineHeight]
            logging.debug("Enough data")
        #Get the lines of the Base Fragment
        lBaseFragmentLine[0] = [lCompareFragmentLine[0][0],
                              lCompareFragmentLine[0][1] - lLineHeight,
                              lCompareFragmentLine[0][2],
                              lCompareFragmentLine[0][3] - lLineHeight]
        if lCompareFragmentLine[1] is not None:
            lBaseFragmentLine[1] = [lCompareFragmentLine[1][0],
                                  lCompareFragmentLine[1][1] - lLineHeight,
                                  lCompareFragmentLine[1][2],
                                  lCompareFragmentLine[1][3] - lLineHeight]
        else:
            lCompareFragmentLine[1] = [0, 0, 0, 0]
            lBaseFragmentLine[1] = [0, 0, 0, 0]

        #According to the Header, enough image data is already in place
        if lBaseFragmentCut[1][X] >= lBaseFragmentImage.size[WIDTH] \
                and lBaseFragmentCut[1][Y] >= lBaseFragmentImage.size[HEIGHT]:
            pPath.mComplete = True
            return 90

        #====== Histogram Intersection =======
        #Histogram of the base fragments last data line
        #lHist1 = lBaseFragmentImage.crop(lBaseFragmentLine[0]).histogram() + \
        #            lBaseFragmentImage.crop(lBaseFragmentLine[1]).histogram()

        #Histogram of the compare fragments last data line
        #lHist2 = lCompareFragmentImage.crop(lCompareFragmentLine[0]).\
        #        histogram() + \
        #        lCompareFragmentImage.crop(
        #                 lCompareFragmentLine[1]).histogram()

        #Do the Histogram intersection
        #lWeight = 0
        #for lIdx in xrange(len(lHist1)):
        #    if abs(lHist1[lIdx] - lHist2[lIdx]) < pOptions.similarity:
        #        lWeight += 1

        #======= Partial Image Matching (PIM) ======
        lPIMScore = 0
        lPixels = 0
        X1 = 0
        Y1 = 1
        X2 = 2
        Y2 = 3
        #Iterate through the first line
        #TODO: more elegance ;)
        #logging.debug("Base Fragment: "+str(lBaseFragmentLine[0])+"/"+
        #           str(lBaseFragmentLine[1]))
        #logging.debug("Comp Fragment: "+str(lCompareFragmentLine[0])+
        #           "/"+str(lCompareFragmentLine[1]))
        lBits = lBaseFragmentImage.bits
        lBaseFragmentImage = lBaseFragmentImage.convert("RGB")
        lCompareFragmentImage = lCompareFragmentImage.convert("RGB")

        #iterate through both comparison lines
        for lLineIdx in xrange(2):
            for lX in xrange(lBaseFragmentLine[lLineIdx][X1],
                               lBaseFragmentLine[lLineIdx][X2]):
                lPx1 = lBaseFragmentImage.getpixel((lX,
                                        lBaseFragmentLine[lLineIdx][Y2]))
                lPx2 = lCompareFragmentImage.getpixel((lX,
                                        lCompareFragmentLine[lLineIdx][Y1]))
                lPIMScore += (abs(lPx1[0] - lPx2[0]) +
                              abs(lPx1[1] - lPx2[1]) +
                              abs(lPx1[2] - lPx2[2])) / 3
                lPixels += 1
        if lPixels != 0:
            lPIMScore = lPIMScore / lPixels
            #percentage of the possible score
            return (2 ** lBits - lPIMScore) * 100 / \
                (2 ** lBits)
        else:
            logging.info("No Pixels: lBaseFragmentLine=" +
                    str(lBaseFragmentLine[0]))
            logging.info("No Pixels: lCompareFragmentLine=" +
                    str(lCompareFragmentLine[0]))
        return 0

    def _determineJpegCut(self, pImage, pVerticalSamplingSize=None):

        X = 0
        Y = 1

        #Convert to Grey Values to determine the border better
        try:
            lImage = pImage.convert("L")
        except IOError:
            #In some rare cases, the first convert throws an error but
            #works afterwards
            lImage = pImage.convert("L")

        PictureEnd = [[-1, -1], [-1, -1]]
        for y in reversed(range(0, pImage.size[Y])):
            #Also look at the neighbors to prevent correct grey pixels
            if not 125 < lImage.getpixel((lImage.size[X] - 1, y)) < 130 or \
               not 125 < lImage.getpixel((lImage.size[X] - 3, y)) < 130 or \
               not 125 < lImage.getpixel((lImage.size[X] - 5, y)) < 130:
                    PictureEnd[0][Y] = y + 1
                    break

        if pVerticalSamplingSize is None:
            pVerticalSamplingSize = 0
            for y in reversed(range(0, pImage.size[Y])):
                #Also look at the neighbors to prevent correct grey pixels
                if not 125 < lImage.getpixel((0, y)) < 130 or \
                   not 125 < lImage.getpixel((3, y)) < 130 or \
                   not 125 < lImage.getpixel((5, y)) < 130:
                        pVerticalSamplingSize = y + 1
                        break
            #Gives the sampling size (height of an encoded JPEG line)
            pVerticalSamplingSize -= PictureEnd[0][Y]

        #There is no cut in the Image
        if(PictureEnd[0][Y] == lImage.size[Y]):
            return [[lImage.size[X], lImage.size[Y] - 15], lImage.size]

        for x in reversed(range(0, lImage.size[X])):
            #Also look at the neighbors to prevent correct grey pixels
            if not 125 < lImage.getpixel((x, PictureEnd[0][Y])) < 130 or \
               not 125 < lImage.getpixel((x, PictureEnd[0][Y] + 2)) < 130 or \
               not 125 < lImage.getpixel((x, PictureEnd[0][Y] + 4)) < 130:
                PictureEnd[0][X] = x + 1
                break
        if PictureEnd[0][X] == -1:
            PictureEnd[0][X] = lImage.size[X]

        PictureEnd[1][X] = PictureEnd[0][X]
        PictureEnd[1][Y] = PictureEnd[0][Y] + \
                pVerticalSamplingSize - 1  # 2*8-1

        return PictureEnd

    #Analyzes the JPEG Fragment for Markers
    def _analyzeJpeg(self, pFile, pData):
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


class CFile(object):

    def __init__(self, pFragmentId):
        self.mFileName = None
        self.mFilePath = None
        self.mDataBegin = -1
        self.mComplete = False
        self.mFragments = []
        self.mFragments.append(pFragmentId)

    def getHeaderFragmentId(self):
        return self.mFragments[0]

    def getLastFragmentId(self):
        return self.mFragments[len(self.mFragments) - 1]

    def addFragmentId(self, pFragmentId):
        self.mFragments.append(pFragmentId)

    def __str__(self):
        return "%s%s " % (self.mFileName, self.mFragments)


class CFileJpeg(CFile):

    MRK_SOS = 0xDA
    MRK_SOI = 0xD8
    MRK_EOI = 0xD9

    def __init__(self, pFragmentId):
        CFile.__init__(self, pFragmentId)
        self.mFileType = "JPEG"
        #All Markers have a relative Position
        self.mMarker = [-1] * 255
        self.mHeaderData = None
        self.mBaseImagePath = None
        #Vertical pixels used in block for DCT (e.g. 8,8 or 16,16)
        self.mVerticalSamplingSize = None
        self.mSize = None
        self.mBits = None

    def addFragmentId(self, pFragmentId):
        CFile.addFragmentId(self, pFragmentId)
        #The calculated Image changed with the new Fragment
        self.mBaseImagePath = None

    def __str__(self):
        return "%s%s (JPEG)" % (self.mFileName, self.mFragments)


class CFileVideo(CFile):

    def __init__(self, pFragmentId):
        CFile.__init__(self, pFragmentId)
        self.mFileType = "Video"
        self.mPicBegin = ""
        self.mPicEnd = ""

    def __str__(self):
        return "%s%s (Video)" % (self.mFileName, self.mFragments)
