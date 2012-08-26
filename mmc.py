# -*- coding: utf-8 -*-

"""The user interface for our app"""


import os
import sys
import platform
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG)

from gui import gui_fc

sys.path.append('.')
if platform.system().lower() == "windows":
    lBits = 32
    if sys.maxsize > 2 ** 32:
        lBits = 64
    lPath = r"collating\fragment\lib\magic\dll" + str(lBits)
    lPath += r";collating\fragment"
    os.environ['PATH'] += ";" + lPath


def main():
    lMain = gui_fc.CMain()
    lMain.run()

if __name__ == "__main__":
    main()
