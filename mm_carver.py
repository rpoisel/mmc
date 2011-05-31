#!/usr/bin/python

# Written by Rainer Poisel <rainer.poisel@fhstp.ac.at>

import sys
import os
import os.path
import subprocess
import optparse

import magic

# import only if necessary
import contexts.media.frag_mm_meta_context
import contexts.tsk.tsk
import lib.datatypes
import block


class CContext():
    default_imagefile = 'image.img'
    default_fragmentsize = 4096
    default_incrementsize = 4096
    default_offset = 0
    default_preprocessing = False

    def __init__(self):
        self.__mMagic = magic.open(magic.MAGIC_NONE)
        self.__mMagic.load()

    def run(self):
        lParser = optparse.OptionParser(add_help_option=False)
        lParser.add_option("-h", "--help", action="help")
        lParser.add_option("-v", action="store_true", dest="verbose",
                help="Be moderately verbose")
        lParser.add_option("-f", "--file", dest="imagefile",
                help="The imagefile (default:" + 
                CContext.default_imagefile + ")",
                default=CContext.default_imagefile)
        lParser.add_option("-s", "--fragmentsize", dest="fragmentsize",
                help="Size of fragments to investigate (default:" +
                str(CContext.default_fragmentsize) + ")",
                default=CContext.default_fragmentsize,
                type="int")
        lParser.add_option("-i", "--incrementsize", dest="incrementsize",
                help="Number of bytes from possible start of fragments" +
                "(default:" + str(CContext.default_incrementsize) + ")",
                default=CContext.default_incrementsize,
                type="int")
        lParser.add_option("-o", "--offset", dest="offset",
                help="Number of bytes to skip at the beginning" +
                " (default:" + str(CContext.default_offset) + ")",
                default=CContext.default_offset,
                type="int")
        lParser.add_option("-p", "--preprocess", action="store_true",
                dest="preprocess",
                help="Turn preprocessing on or off" +
                " (default:" + str(CContext.default_preprocessing) + ")",
                default=CContext.default_preprocessing)
        (lOptions, lArgs) = lParser.parse_args()

        try:
            lH264Headers = []
            lMapOfBlocks = []

            # open imagefile
            lImage = open(lOptions.imagefile, "rb")
            lOffset = lOptions.offset
            lIncrementSize = lOptions.incrementsize
            
            # TODO pre-processing: check where to start carving
            # use TSK (http://www.sleuthkit.org/) for that purpose
            if lOptions.preprocess == True:
                #lTSK = tsk.CTSK(lImage)
                #lH264Headers = lTSK.parseH264Headers()
                #lH264Fragments = lTSK.parseH264Fragments()
                lTSK = tsk.CTSK(lMapOfBlocks)
                lOffset = lTSK.getOffset()
                lIncrementSize = lTSK.getIncrementSize()

            # work directly on the image
            else:
                #lPlain = plain.CPlain(lImage)
                #lH264Headers = lTSK.parseH264Headers()
                #lH264Fragments = lTSK.parseH264Fragments()

                lImage.seek(lOptions.offset, os.SEEK_SET)

                # collating: walk through fragments of the file 
                while True:
                    lBuffer = lImage.read(lOptions.fragmentsize)
                    if lBuffer == "":
                        break;

                    # check for beginning of files using libmagic(3)
                    lType = self.__mMagic.buffer(lBuffer)
                    if lType.find("H.264") >= 0 and lType.find("video") >= 0:
                        lH264Headers.append(lOffset)
                    # generate a map of filetypes of fragments

                    # position internal file pointer
                    lOffset += lIncrementSize
                    lImage.seek(lOffset, os.SEEK_SET)

            print(lH264Headers)

            # close file
            lImage.close()
            
            # TODO reassembly: 
            
        except LookupError, pExc:
            print("Error: " + str(pExc))
            sys.exit(-1)
        except NameError, pExc:
            print("Error: " + str(pExc))
            sys.exit(-2)
        except EOFError, pExc:
            sys.exit(-3)
        except Exception, pExc:
            print("Error: " + str(pExc))
            sys.exit(-4)

if __name__ == "__main__":
    lContext = CContext()
    lContext.run()
