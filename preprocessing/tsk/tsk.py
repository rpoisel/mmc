import os
import logging
import subprocess
from tsk_cmd import CTSKblkls
import gui.gui_options


class CGeneratorContext:
    def __init__(self, start, stop):

        self.__pOptions = gui.gui_options.CGuiOptions()
        self.__mImage = open(self.__pOptions.imagefile, "rb")
        self.__start = start
        self.__stop = stop

        self.__clusterarea = 0
        self.__rootdir = 0

        for key in self.__pOptions.tskProperties.iterkeys():
            if key.lower().find("cluster area") >= 0:
                self.__clusterarea = self.__pOptions.tskProperties[key]\
                                [:self.__pOptions.tskProperties[key].find(" ")]
            if key.lower().find("root directory") >= 0:
                self.__rootdir = self.__pOptions.tskProperties[key]\
                               [:self.__pOptions.tskProperties[key].find(" ")]

    def __del__(self):
        self.__mImage.close()

    def __createGenerator(self):

        lBlkLs = CTSKblkls()
        lBlkLs.filename = self.__pOptions.imagefile
        lBlkLs.imageoffset = self.__pOptions.imageoffset
        lBlkLs.fstype = self.__pOptions.fstype
        lBlkLs.sectorsize = self.__pOptions.fragmentsize
        lBlkLs.list = True
        lBlkLs.start = self.__start
        lBlkLs.stop = self.__stop

        if self.__pOptions.blockstatus == "allocated":
            command = lBlkLs.getAllocated()
        elif self.__pOptions.blockstatus == "unallocated":
            command = lBlkLs.getUnallocated()
        else:
            raise Exception, "Wrong value for blockstatus!"

        logging.info("Executing command: " + str(command))

        proc = subprocess.Popen(command, stdout=subprocess.PIPE)

        for i in range(3):
                line = proc.stdout.readline()

        self.__mFragsChecked = 0

        while True:
            line = proc.stdout.readline()
            if not line:
                break
            else:
                lOffset = self.__getOffset(line, '')
                logging.info("Seeking to offset " + str(lOffset))
                self.__mImage.seek(lOffset, os.SEEK_SET)
                lBuffer = self.__mImage.read(self.__pOptions.fragmentsize)

                self.__mFragsChecked += 1

                if not lBuffer:
                    break

                yield (lOffset, lBuffer)

    def __getOffsetFat(self, line):
        return (int(line[:line.find('|')]) - 2) * \
            self.__pOptions.fragmentsize + int(self.__clusterarea) * 512

    def __getOffsetNtfs(self, line):
        return (int(line[:line.find('|')])) * self.__pOptions.fragmentsize

    def __getOffset(self, line, filesystem):
        if self.__pOptions.fstype.lower().find("ntfs") >= 0:
            return self.__getOffsetNtfs(line)
        elif self.__pOptions.fstype.lower().find("fat") >= 0:
            return self.__getOffsetFat(line)
        else:
            raise Exception, "Filesystem not implemented!"

    def getFragsRead(self):
        return 1

    def getFragsTotal(self):
        return 1

    def getGenerator(self):
        return self.__createGenerator()


class CTskImgProcessor:
    def __init__(self, pOptions):
        self.__mGenerators = []
        self.__mNumParallel = pOptions.maxcpus
        self.__mFsType = pOptions.fstype

        if self.__mFsType.lower().find("ntfs") >= 0:
            clusterrange = pOptions.tskProperties["Total Cluster Range"]
            lsize = int(clusterrange[clusterrange.find("-") + 1:].strip())
        elif self.__mFsType.lower().find("fat") >= 0:
            clusterrange = pOptions.tskProperties["* Data Area"]
            lsize = int(clusterrange[clusterrange.find("-") + 1:].strip())
        else:
            start = 0
            stop = 1
            self.__mGenerators.append(CGeneratorContext(start, stop))
            return

        lBlockRange = lsize // self.__mNumParallel

        ranges = []
        for i in range(self.__mNumParallel):
            ranges.append(lBlockRange * (i + 1))

        rest = lsize % self.__mNumParallel
        if rest > 0:
            ranges[len(ranges) - 1] += rest

        rangestart = 0
        for lPid in range(self.__mNumParallel):
            start = rangestart
            stop = ranges[lPid] - 1
            rangestart = ranges[lPid]
            self.__mGenerators.append(CGeneratorContext(start, stop))

    def getNumParallel(self, pNumParallel):
        return pNumParallel

    def getFragsRead(self, pPid):
        return self.__mGenerators[pPid].getFragsRead()

    def getFragsTotal(self, pPid):
        return self.__mGenerators[pPid].getFragsTotal()

    def getGenerator(self, pPid):
        return self.__mGenerators[pPid].getGenerator()
