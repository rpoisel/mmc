import os
import os.path
import logging
import sys

import magic

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    lMagic = magic.open(magic.MAGIC_NONE)
    lMagic.load()
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        logging.info("Usage: " + sys.argv[0] + " <dir> <file-type> <action>")
        sys.exit(-1)
    lDir = sys.argv[1]
    lFiletype = sys.argv[2]
    lAction = "none"
    if len(sys.argv) == 4:
        lAction = sys.argv[3]
    for lDirEnt in os.listdir(lDir):
        lPath = lDir + os.sep + lDirEnt
        if os.path.isfile(lPath) and lMagic.file(lPath).lower().find(lFiletype) == -1:
            if lAction == '-d':
                os.remove(lPath)
            else:
                logging.info("Not removing: " + lPath)
