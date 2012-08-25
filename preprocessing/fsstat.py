import subprocess
import os
import os.path
import platform


class CFsOptions:

    def __init__(self, pSize=0, pOffset=0, pIncrement=512,
            pBlockSize=512, pSectorSize=512, pFsType='',
            pTskProperties={}):
        self.size = pSize
        self.offset = pOffset
        self.increment = pIncrement
        self.blocksize = pBlockSize
        self.sectorsize = pSectorSize
        self.fstype = pFsType
        self.tskProperties = pTskProperties

    def __str__(self):
        lString = str(self.size) + " bytes, " + \
                self.fstype if self.fstype != '' else 'N/A'
        lString += ", block size = " + str(self.blocksize) + \
                    ", offset = " + str(self.offset)
        return lString


class CFsStat:
    @staticmethod
    def getFsGeometry(pOptions):
        lSize = os.path.getsize(pOptions.imagefile)
        # dirty hack
        lTsk = None
        if platform.system().lower() == 'windows':
            lTsk = subprocess.Popen(['bin' + os.sep + 'fsstat.exe',
                pOptions.imagefile], bufsize=512, stdout=subprocess.PIPE)
        else:
            lTsk = subprocess.Popen(['fsstat', pOptions.imagefile],
                    bufsize=512, stdout=subprocess.PIPE)
        lTskOutput = lTsk.communicate()
        lTskProperties = {}
        for lPair in [lElem for lElem in [lLine.split(': ')
                for lLine in lTskOutput[0].split('\n')] if len(lElem) == 2]:
            lTskProperties[lPair[0].strip()] = lPair[1].strip()

        lBlockSize = lTskProperties["Cluster Size"] \
                if "Cluster Size" in lTskProperties else "512"
        lSectorSize = lTskProperties["Sector Size"] \
                if "Sector Size" in lTskProperties else "512"

        if "* Data Area" in lTskProperties:
            # first sector index * sector size (512 bytes)
            lOffset = int(lTskProperties['* Data Area'].split(' - ')[0]) * 512
        else:
            lOffset = 0

        return CFsOptions(pSize=lSize,
                pOffset=lOffset,
                pBlockSize=lBlockSize,
                pIncrement=lBlockSize,
                pFsType=lTskProperties["File System Type"] if
                        "File System Type" in lTskProperties else '',
                pTskProperties=lTskProperties)
