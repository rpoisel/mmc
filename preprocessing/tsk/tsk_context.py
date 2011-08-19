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
        self.__start = pOptions.start
        self.__stop = pOptions.stop
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
        lBlkLs.start = self.__start
        lBlkLs.stop = self.__stop
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
        self.__mNumParallel = pOptions.maxcpus
        self.__mNumParallel = 1

        clusterrange = pOptions.tskProperties["Total Cluster Range"]
        lsize = int(clusterrange[clusterrange.find("-") + 1:].strip())
        
        lBlockRange = lsize // self.__mNumParallel
        ranges = []
        for i in range(self.__mNumParallel):
            ranges.append(lBlockRange * (i +1))
        
        rest = lsize % self.__mNumParallel
        if rest > 0:
            ranges[len(ranges)-1] += rest
        
        print ranges        
        
        rangeindex = 0
        rangestart = 0
        rangestop = 0
        add = 1
        for lPid in range(self.__mNumParallel):
            pOptions.start = rangestart
            pOptions.stop = ranges[lPid] -1
            rangestart = ranges[lPid]
            
            self.__mGenerators.append(CGeneratorContext(pOptions))


    def getNumParallel(self):
        return self.__mNumParallel

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
