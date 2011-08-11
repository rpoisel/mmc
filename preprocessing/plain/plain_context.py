import os

from collating.fragment import fragment_context

class CGeneratorContext:
    def __init__(self, pPathImage, pOffset, pSize, pFragmentSize, pIncrementSize):
        self.__mImage = open(pPathImage, "rb")
        self.__mOffset = pOffset
        self.__mSize = pSize
        self.__mFragmentSize = pFragmentSize
        self.__mIncrementSize = pIncrementSize
        self.__mFragsChecked = 0
        self.__mFragsTotal = 0
        print("Offset = " + str(self.__mOffset) + ", Size = " + \
                str(self.__mSize))

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):
        # calculate size of investigated data area
        lSize = self.__mSize
        lOffset = self.__mOffset
        # TODO catch IOError if illegal offset has been given
        self.__mImage.seek(lOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        self.__mFragsTotal = lSize / self.__mFragmentSize
        if lSize % self.__mFragmentSize != 0:
            self.__mFragsTotal += 1

        lCntFrag = 0

        while True:
            if lCntFrag >= self.__mFragsTotal:
                break
            lCntFrag += 1
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
        return self.__createGenerator()

class CPlainImgProcessor:
    def __init__(self, pOptions):
        self.__mGenerators = []
        lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
        print("Size = " + str(lSize))
        for lPid in range(pOptions.maxcpus):
            self.__mGenerators.append(CGeneratorContext(
                pOptions.imagefile, \
                pOptions.offset  + lPid * lSize / pOptions.maxcpus, \
                lSize / pOptions.maxcpus, \
                pOptions.fragmentsize, \
                pOptions.incrementsize))

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
