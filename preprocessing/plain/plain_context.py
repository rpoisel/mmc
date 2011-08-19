import os
import logging
import math

#from collating.fragment import fragment_context

class CGeneratorContext:
    def __init__(self, pPathImage, pOffset, pNumFrags, pFragmentOffset, \
            pFragmentSize, pIncrementSize):
        self.__mImage = open(pPathImage, "rb")
        self.__mOffset = pOffset
        self.__mNumFrags = pNumFrags
        self.__mFragmentOffset = pFragmentOffset
        self.__mFragmentSize = pFragmentSize
        self.__mIncrementSize = pIncrementSize
        logging.info("Offset = " + str(self.__mFragmentOffset) + ", NumFrags = " + \
                str(self.__mNumFrags))

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):
        # calculate size of investigated data area
        lOffset = self.__mOffset + self.__mFragmentOffset * self.__mFragmentSize
        # TODO catch IOError if illegal offset has been given
        self.__mImage.seek(lOffset, os.SEEK_SET)

        lCntFrag = 0

        while True:
            if lCntFrag >= self.__mNumFrags:
                break
            lCntFrag += 1
            lBuffer = self.__mImage.read(self.__mFragmentSize)
            if lBuffer == "":
                break
            
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
        self.__mNumParallel = pOptions.maxcpus
        lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
        # collating: walk through fragments of the file
        lFragsTotal = lSize / pOptions.fragmentsize
        if lSize % pOptions.fragmentsize != 0:
            lFragsTotal += 1
        lFragsPerCpu = int(math.ceil(float(lFragsTotal)/self.__mNumParallel))
        lFragsPerCpuR = lFragsTotal % lFragsPerCpu
        for lPid in range(self.__mNumParallel):
            self.__mGenerators.append(CGeneratorContext(
                pOptions.imagefile, \
                pOptions.offset, \
                lFragsPerCpuR if lPid is (self.__mNumParallel - 1) and lFragsPerCpuR > 0 else lFragsPerCpu, \
                lFragsPerCpu * lPid, 
                pOptions.fragmentsize, \
                pOptions.incrementsize))

    def getNumParallel(self):
        return self.__mNumParallel

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
