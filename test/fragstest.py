import sys
import logging
import datetime

from lib import frags
from reassembly.fragmentizer import fragmentizer_context

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    lHeadersTxt = sys.argv[1]
    lBlocksTxt = sys.argv[2]

    lFrags = frags.CFrags()
    
    lHeadersFH = open(lHeadersTxt, 'r')
    lBlocksFH = open(lBlocksTxt, 'r')

    while True:
        lLine = lHeadersFH.readline()
        if lLine == '':
            break
        lFrags.addHeader(int(lLine.strip()))
    while True:
        lLine = lBlocksFH.readline()
        if lLine == '':
            break
        lFrags.addBlock(int(lLine.strip()))
    
    logging.info("Starting fragmentizing.")
    lFragmentizer = fragmentizer_context.CFragmentizer()
    lH264Fragments = lFragmentizer.defrag(lFrags, 
            512, 16384,
            4)
    logging.info("Finished fragmentizing.")
    logging.info("8<=============== FRAGMENTs ==============")
    for lIdx in xrange(len(lH264Fragments)):
        lH264Fragment = lH264Fragments[lIdx]
        logging.info("FragmentIdx %04d" % lIdx + ": " + str(lH264Fragment))
    logging.info("8<=============== FRAGMENTs ==============")

    lHeadersFH.close()
    lBlocksFH.close()
