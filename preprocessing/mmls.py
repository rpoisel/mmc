from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT


class CMmls(object):

    def __init__(self):
        super(CMmls, self).__init__()

    def getPartitions(self, pSource):
        lOutput = Popen(["mmls", pSource],
                stdout=PIPE,
                stderr=STDOUT).communicate()
        return lOutput[0]
