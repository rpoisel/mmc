import os
import logging
import subprocess
import math
from tsk import CTSKblkls

class CGeneratorContext:
    def __init__(self, pOptions):
        self.__mImage = open(pOptions.imagefile, "rb")
        self.__mPathImage = pOptions.imagefile
        self.__mImageOffset = pOptions.imageoffset
        self.__mOffset = pOptions.offset
        #self.__mNumFrags = pNumFrags
        #self.__mFragmentOffset = pFragmentOffset
        self.__mFragmentSize = pOptions.fragmentsize
        self.__mIncrementSize = pOptions.incrementsize
        self.__mFsType = pOptions.fstype
        #logging.info("Offset = " + str(self.__mFragmentOffset) + ", NumFrags = " + \
                #str(self.__mNumFrags))

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):
        
        lBlkLs = CTSKblkls()
        lBlkLs.filename = self.__mPathImage
        lBlkLs.imageoffset = self.__mImageOffset
        lBlkLs.fstype = self.__mFsType
        #lBlkLs.imagetype = ''
        lBlkLs.sectorsize = self.__mFragmentSize
        lBlkLs.list = True
        lBlkLs.start = -1
        lBlkLs.stop = -1
        command = lBlkLs.getAllocated()
        
        logging.info("Executing command: " + str(command))
        
        proc = subprocess.Popen(command,stdout=subprocess.PIPE)
        
        for i in range(3):
                line = proc.stdout.readline()
                
        #self.__mFragsChecked = 0

        while True:
            line = proc.stdout.readline()
            if not line:
                break
            else:
                
                lOffset = self.__getOffset(line, '')
                # TODO catch IOError if illegal offset has been given
                logging.info("Seeking to offset " + str(lOffset))
                self.__mImage.seek(lOffset, os.SEEK_SET)
                lBuffer = self.__mImage.read(self.__mFragmentSize)
                
                if not lBuffer:
                    break
                
                yield (lOffset, lBuffer)
                    
                #self.__mFragsChecked += 1
                #self.__mFragsTotal += 1

    def __getOffsetFat(self, line):
        return (int(line[:line.find('|')])) * self.__mFragmentSize + (self.__mOffset - self.__mFragmentSize)
    
    def __getOffsetNtfs(self, line):
        return (int(line[:line.find('|')])) * self.__mFragmentSize
        
    def __getOffset(self, line, filesystem):
        if self.__mFsType.lower().find("ntfs") >= 0:
            return self.__getOffsetNtfs(line)
        elif self.__mFsType.lower().find("fat") >= 0:
            return self.__getOffsetFat(line)

    def getFragsRead(self): 
        #return self.__mFragsChecked
        return 1

    def getFragsTotal(self): 
        #return self.__mFragsTotal
        return 1

    def getGenerator(self): 
        return self.__createGenerator()

class CTskImgProcessor:
    def __init__(self, pOptions):
        self.__mGenerators = []
        #self.__mNumParallel = pOptions.maxcpus
        self.__mNumParallel = 1

#        lSize = os.path.getsize(pOptions.imagefile) - pOptions.offset
#         collating: walk through fragments of the file
#        lFragsTotal = lSize / pOptions.fragmentsize
#        if lSize % pOptions.fragmentsize != 0:
#            lFragsTotal += 1
#        lFragsPerCpu = int(math.ceil(float(lFragsTotal)/self.__mNumParallel))
#        lFragsPerCpuR = lFragsTotal % lFragsPerCpu
        for lPid in range(self.__mNumParallel):
            self.__mGenerators.append(CGeneratorContext(pOptions))
#                pOptions.imagefile, \
#                pOptions.offset, \
#                -1, #lFragsPerCpuR if lPid is (self.__mNumParallel - 1) and lFragsPerCpuR > 0 else lFragsPerCpu, \
#                -1, #lFragsPerCpu * lPid, 
#                pOptions.fragmentsize, \
#                pOptions.incrementsize))

    def getNumParallel(self):
        return self.__mNumParallel

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
