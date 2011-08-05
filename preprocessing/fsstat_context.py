import subprocess
import os.path

class CFsOptions:

    def __init__(self, pSize = 0, pOffset = 0, pIncrement = 512, pBlockSize = 512, pFsType = "N/A"):
        self.size = pSize
        self.offset = pOffset
        self.increment = pIncrement
        self.blocksize = pBlockSize
        self.fstype = pFsType

    def __str__(self):
        lString = str(self.size) + " bytes, " + \
                self.fstype + \
                    ", block size = " + str(self.blocksize) + \
                    ", offset = " + str(self.offset)
        return lString

class CFsStatContext:
    @staticmethod
    def getFsGeometry(pOptions):
        lSize = os.path.getsize(pOptions.imagefile)
        # dirty hack
        lTsk = subprocess.Popen(['fsstat', pOptions.imagefile], bufsize=512, stdout=subprocess.PIPE)
        lTskOutput = lTsk.communicate()
        lTskProperties = {}
        for lPair in [lElem for lElem in [lLine.split(': ') for lLine in lTskOutput[0].split('\n')] if len(lElem) == 2]:
            lTskProperties[lPair[0].strip()] = lPair[1].strip()

        lBlockSize = lTskProperties["Cluster Size"] if "Cluster Size" in lTskProperties else "512"

        if "* Data Area" in lTskProperties:
            # first sector index * sector size (512 bytes)
            lOffset = int(lTskProperties['* Data Area'].split(' - ')[0]) * 512
        else:
            lOffset = 0

        return CFsOptions(pSize = lSize,
                pOffset = lOffset,
                pBlockSize = lBlockSize,
                pIncrement = lBlockSize,
                pFsType = lTskProperties["File System Type"] if "File System Type" in lTskProperties else "N/A")

