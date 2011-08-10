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
        self.__mGenerators = []
        self.__mFragsChecked = []
        self.__mFragsTotal = []
        self.__mNumCPUs = pOptions.maxcpus
        for lPid in range(self.__mNumCPUs):
            self.__mFragsChecked.append(0)
            self.__mFragsTotal.append(0)
            self.__mGenerators.append(self.__createGenerator(lPid))

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self, pPid):
        # calculate size of investigated data area
        lSize = self.__mSize - self.__mOffset
        lOffset = self.__mOffset + pPid * lSize / self.__mNumCPUs
        # TODO catch IOError if illegal offset has been given
        self.__mImage.seek(lOffset, os.SEEK_SET)

        # collating: walk through fragments of the file
        self.__mFragsTotal[pPid] = lSize / (self.__mFragmentSize * self.__mNumCPUs)
        if (lSize / self.__mNumCPUs) % self.__mFragmentSize != 0:
            self.__mFragsTotal[pPid] += 1

        while True:
            lBuffer = self.__mImage.read(self.__mFragmentSize)
            if lBuffer == "":
                break
            
            self.__mFragsChecked[pPid] += 1

            yield (lOffset, lBuffer)

            lOffset += self.__mIncrementSize
            self.__mImage.seek(lOffset, os.SEEK_SET)


    def getFragsRead(self, pPid):
        return self.__mFragsChecked[pPid]

    def getFragsTotal(self, pPid):
        return self.__mFragsTotal[pPid]

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid]
