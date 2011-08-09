import os
import subprocess
from collating.magic import magic_context


class CTSKImgProcessor:
    def __init__(self, pOptions):
        # TODO create accessors
        self.__mOffset = pOptions.offset
        self.__mIncrementSize = pOptions.incrementsize
        self.__mFragmentSize = pOptions.fragmentsize

        self.__mImage = open(pOptions.imagefile, "rb")
        self.__mImageFileName = pOptions.imagefile
        self.__mSize = os.path.getsize(pOptions.imagefile)
        if pOptions.blockstatus == "allocated":
            self.__mBlockStatus = "-a"
        else:
            self.__mBlockStatus = "-A"
        self.__mGenerator = self.__createGenerator()

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):
        
        print self.__mImageFileName
        
        proc = subprocess.Popen(['blkls', \
                self.__mBlockStatus, '-l', \
                self.__mImageFileName],stdout=subprocess.PIPE)
        # ignore the first three lines
        for lCnt in range(3):
            line = proc.stdout.readline()
        
        self.__mFragsChecked = 0
        self.__mFragsTotal = 0

        # collating: walk through fragments of the file
        if self.__mSize % self.__mFragmentSize != 0:
            self.__mFragsTotal += 1

        while True:
            line = proc.stdout.readline()
            #print line
            if line != '':
                lOffset = (int(line[:line.find('|')])) * self.__mFragmentSize
                # TODO catch IOError if illegal offset has been given
                self.__mImage.seek(lOffset, os.SEEK_SET)
                lBuffer = self.__mImage.read(self.__mFragmentSize)
                
                if lBuffer == "":
                    break
                
                self.__mFragsChecked += 1
                self.__mFragsTotal += 1
                yield (lOffset, lBuffer)
    
                #lOffset = int(line[:line.find('|')]) * 4096
                #self.__mImage.seek(lOffset, os.SEEK_SET)
            else:
                break


    def getFragsRead(self):
        #return self.__mFragsChecked
        return 0

    def getFragsTotal(self):
        return self.__mFragsTotal

    def getGenerator(self):
        return self.__mGenerator
