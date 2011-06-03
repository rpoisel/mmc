import os

from contexts.fragment import fragment_context
from contexts.magic import magic_context


class CPlain:
    def __init__(self, pImage):
        self.__mImage = pImage
        self.__mMagic = magic_context.CMagic()
        self.__mH264FC = fragment_context.CFragmentClassifier("bla")

    def parseH264(self, pH264HeadersList, pH264BlocksList,
            pOffset, pIncrementSize, pFragmentSize):
        self.__mImage.seek(pOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        while True:
            lBuffer = self.__mImage.read(pFragmentSize)
            if lBuffer == "":
                break

            # check for beginning of files using libmagic(3)
            if self.__mMagic.determineMagicH264(lBuffer) == True:
                pH264HeadersList.append(pOffset)
                #pH264BlocksList.append(pOffset)

            # generate a map of filetypes of fragments
            if self.__mH264FC.classify(lBuffer) > 0:
                pH264BlocksList.append(pOffset)

            # position internal file pointer
            pOffset += pIncrementSize
            self.__mImage.seek(pOffset, os.SEEK_SET)
