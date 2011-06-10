import os

from collating.fragment import fragment_context
from collating.magic import magic_context


class CPlain:
    def __init__(self, pImageFile):
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier("<path>")
        self.__mImage = open(pImageFile, "rb")

    def __del__(self):
        self.__mImage.close()

    def parseH264(self, pH264Fragments, 
            pOffset, pIncrementSize, pFragmentSize):
        self.__mImage.seek(pOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        while True:
            lBuffer = self.__mImage.read(pFragmentSize)
            if lBuffer == "":
                break

            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBuffer) == True:
                pH264Fragments.addHeader(pOffset)

            # generate a map of filetypes of fragments
            if self.__mH264FC.classify(lBuffer) > 0:
                pH264Fragments.addBlock(pOffset)

            # position internal file pointer
            pOffset += pIncrementSize
            self.__mImage.seek(pOffset, os.SEEK_SET)
