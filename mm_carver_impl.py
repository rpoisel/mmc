#!/usr/bin/python

import optparse

from mm_context import CContext

if __name__ == "__main__":
    lParser = optparse.OptionParser(add_help_option=False)
    lParser.add_option("-h", "--help", action="help")
    lParser.add_option("-v", action="store_true", dest="verbose",
            help="Be moderately verbose")
    lParser.add_option("-f", "--file", dest="imagefile",
            help="The imagefile (default:" +
            CContext.sDefaultImagefile + ")",
            default=CContext.sDefaultImagefile)
    lParser.add_option("-s", "--fragmentsize", dest="fragmentsize",
            help="Size of fragments to investigate (default:" +
            str(CContext.sDefaultFragmentsize) + ")",
            default=CContext.sDefaultFragmentsize,
            type="int")
    lParser.add_option("-i", "--incrementsize", dest="incrementsize",
            help="Number of bytes from possible start of fragments" +
            "(default:" + str(CContext.sDefaultIncrementsize) + ")",
            default=CContext.sDefaultIncrementsize,
            type="int")
    lParser.add_option("-e", "--offset", dest="offset",
            help="Number of bytes to skip at the beginning" +
            " (default:" + str(CContext.sDefaultOffset) + ")",
            default=CContext.sDefaultOffset,
            type="int")
    lParser.add_option("-p", "--preprocess", action="store_true",
            dest="preprocess",
            help="Turn preprocessing on or off" +
            " (default:" + str(CContext.sDefaultPreprocessing) + ")",
            default=CContext.sDefaultPreprocessing)
    lParser.add_option("-o", "--output", dest="output",
            help="The output directory for extracted information" +
            " (default:" + str(CContext.sDefaultOutput) + ")",
            default=CContext.sDefaultOutput)
    (lOptions, lArgs) = lParser.parse_args()

    lContext = CContext()
    lContext.run(lOptions)
