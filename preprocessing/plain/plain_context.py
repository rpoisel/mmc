import os

from collating.fragment import fragment_context


class CPlainImgProcessor:
    def __init__(self, pOptions):
        # TODO create accessors
        self.__mOffset = pOptions.offset
        self.__mIncrementSize = pOptions.incrementsize
        self.__mFragmentSize = pOptions.fragmentsize

        self.__mImage = open(pOptions.imagefile, "rb")
        self.__mSize = os.path.getsize(pOptions.imagefile)
        self.__mGenerator = self.__createGenerator()

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):
        self.__mFragsChecked = 0
        lOffset = self.__mOffset
        # TODO catch IOError if illegal offset has been given
        self.__mImage.seek(lOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        self.__mFragsTotal = self.__mSize / self.__mFragmentSize
        if self.__mSize % self.__mFragmentSize != 0:
            self.__mFragsTotal += 1

        while True:
            lBuffer = self.__mImage.read(self.__mFragmentSize)
            if lBuffer == "":
                break
            
            self.__mFragsChecked += 1

            yield (lOffset, lBuffer)

            lOffset += self.__mIncrementSize
            self.__mImage.seek(lOffset, os.SEEK_SET)


    def getFragsRead(self):
        return self.__mFragsChecked

    def getFragsTotal(self):
        return self.__mFragsTotal

    def getGenerator(self):
        return self.__mGenerator
