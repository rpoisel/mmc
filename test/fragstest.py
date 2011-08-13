import sys
import datetime

from lib import frags
from reassembly.fragmentizer import fragmentizer_context

if __name__ == "__main__":

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
    
    print(str(datetime.datetime.now()) + " Starting fragmentizing.")
    lFragmentizer = fragmentizer_context.CFragmentizer()
    lH264Fragments = lFragmentizer.defrag(lFrags, 
            512, 16384,
            4)
    print(str(datetime.datetime.now()) + " Finished fragmentizing.")
    print("8<=============== FRAGMENTs ==============")
    for lIdx in xrange(len(lH264Fragments)):
        lH264Fragment = lH264Fragments[lIdx]
        print("FragmentIdx %04d" % lIdx + ": " + str(lH264Fragment))
    print("8<=============== FRAGMENTs ==============")

    lHeadersFH.close()
    lBlocksFH.close()
