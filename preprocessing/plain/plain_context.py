import os
import logging
import math
import platform

#from collating.fragment import fragment_context

class CGeneratorContext:
    def __init__(self, pPathImage, pOffset, pNumFrags, pFragmentOffset, \
            pFragmentSize, pIncrementSize):
        self._mPathImage = pPathImage
        # TODO dirty hack to make it working with linux
        self._mImage = None
        if platform.system().lower() == "linux":
            self._mImage = open(self._mPathImage, "rb")
        self._mOffset = pOffset
        self._mNumFrags = pNumFrags
        self._mFragmentOffset = pFragmentOffset
        self._mFragmentSize = pFragmentSize
        self._mIncrementSize = pIncrementSize
        logging.info("Offset = " + str(self._mFragmentOffset) + ", NumFrags = " + \
                str(self._mNumFrags))
        self._mCntFrag = 0

    def __getstate__(self):
        return self.__dict__
        
    def __setstate__(self, pDict):
        logging.info("Setting state.")
        self._mImage = open(pDict['_mPathImage'], "rb")
        self._mOffset = pDict['_mOffset']
        self._mNumFrags = pDict['_mNumFrags']
        self._mFragmentOffset = pDict['_mFragmentOffset']
        self._mFragmentSize = pDict['_mFragmentSize']
        self._mIncrementSize = pDict['_mIncrementSize']
        self._mCntFrag = pDict['_mCntFrag']
 
    def __del__(self):
        if hasattr(self, '_mImage') and self._mImage != None and \
            self._mImage.closed is False:
                logging.info("Closing file object: " + str(self._mImage))
                self._mImage.close()

    def _createGenerator(self):
        # calculate size of investigated data area
        lOffset = self._mOffset + self._mFragmentOffset * self._mFragmentSize
        # TODO catch IOError if illegal offset has been given
        self._mImage.seek(lOffset, os.SEEK_SET)

        while True:
            if self._mCntFrag >= self._mNumFrags:
                break
            self._mCntFrag += 1
            lBuffer = self._mImage.read(self._mFragmentSize)
            if lBuffer == "":
                break
            
            yield (lOffset, lBuffer)

            lOffset += self._mIncrementSize
            self._mImage.seek(lOffset, os.SEEK_SET)

    def getFragsRead(self): 
        return self._mCntFrag

    def getFragsTotal(self):
        return self._mNumFrags

    def getGenerator(self): 
        return self._createGenerator()

class CPlainImgProcessor:
    def __init__(self, pOptions):
        self.__mGenerators = []
        self.__mNumParallel = pOptions.maxcpus
        lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
        # collating: walk through fragments of the file
        self.__mFragsTotal = lSize / pOptions.fragmentsize
        if lSize % pOptions.fragmentsize != 0:
            self.__mFragsTotal += 1
        lFragsPerCpu = int(math.ceil(float(self.__mFragsTotal)/self.__mNumParallel))
        lFragsPerCpuR = self.__mFragsTotal % lFragsPerCpu
        for lPid in range(self.__mNumParallel):
            self.__mGenerators.append(CGeneratorContext(
                pOptions.imagefile, \
                pOptions.offset, \
                lFragsPerCpuR if lPid is (self.__mNumParallel - 1) and lFragsPerCpuR > 0 else lFragsPerCpu, \
                lFragsPerCpu * lPid, 
                pOptions.fragmentsize, \
                pOptions.incrementsize))

    def getNumParallel(self, pNumParallel):
        return pNumParallel

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
