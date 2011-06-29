import os

from collating.fragment import fragment_context
from collating.magic import magic_context


class CPlain:
    def __init__(self, pImageFile,
            pOffset, pIncrementSize, pFragmentSize):
        self.__mOffset = pOffset
        self.__mIncrementSize = pIncrementSize
        self.__mFragmentSize = pFragmentSize
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier("<path>",
                pFragmentSize)
        self.__mImage = open(pImageFile, "rb")
        self.__mSize = os.path.getsize(pImageFile)

    def __del__(self):
        self.__mImage.close()

    def parseH264(self, pH264Blocks, pCaller = None):
        lFragsChecked = 0
        lOffset = self.__mOffset
        self.__mImage.seek(lOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        lFragsTotal = self.__mSize / self.__mFragmentSize
        if self.__mSize % self.__mFragmentSize != 0:
            lFragsTotal += 1

        while True:
            if pCaller != None and lFragsChecked > 0:
                pCaller.progressCallback(90 * lFragsChecked / lFragsTotal)

            lBuffer = self.__mImage.read(self.__mFragmentSize)
            if lBuffer == "":
                break

            lFragsChecked += 1

            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBuffer) == True:
                pH264Blocks.addHeader(lOffset)

            # TODO ignore header fragments from other identifiable file types

            # generate a map of filetypes of fragments
            elif self.__mH264FC.classify(lBuffer) > 0:
                pH264Blocks.addBlock(lOffset)

            # position internal file pointer
            lOffset += self.__mIncrementSize
            self.__mImage.seek(lOffset, os.SEEK_SET)

        pCaller.finishedCallback()

        return lFragsChecked
