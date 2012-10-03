import re
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT


class CMmls(object):

    def __init__(self, pSource):
        super(CMmls, self).__init__()

        # initialize variables
        self.mPartitions = []
        self.mUnitsize = -1
        self.mOutput = ""

        # execute mmls command
        self.mOutput = Popen(["mmls", pSource],
                stdout=PIPE,
                stderr=STDOUT).communicate()[0]

        # regex unitsize from mmls output
        lRegexUnitsize = re.compile('^Units are in (\d+)-byte sectors$',
                re.MULTILINE)
        lMatch = lRegexUnitsize.search(self.mOutput)
        if lMatch is not None and len(lMatch.groups()) > 0:
            self.mUnitsize = lMatch.group(1)

        # regex partitions from mmls output
        lRegexPartitions = re.compile('\d+:\s+[\w\-:]+\s+0+(\d+)\s+0+(\d+)'
                '\s+0+(\d+)\s+(.*)',
                re.MULTILINE)
        self.mPartitions = lRegexPartitions.findall(self.mOutput)

    def getPartitions(self):
        return self.mPartitions

    def getUnitsize(self):
        return self.mUnitsize

    def getOutput(self):
        return self.mOutput
