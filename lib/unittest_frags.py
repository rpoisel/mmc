#!/usr/bin/env python

import unittest

import frags


class CTestFrags(unittest.TestCase):
    def test_frags_and_headers(self):
        lNumHeaders = 1000
        lNumIter = 2
        lFrags = frags.CFrags()
        for lIter in xrange(lNumIter):
            for lOffset in xrange(lNumHeaders):
                lFrags.addHeader(lOffset)
        self.assertEquals(len(lFrags.getHeaders()), len(lFrags.getBlocks()))
        self.assertEquals(lFrags.getHeaders()[20], lFrags.getBlocks()[20])

if __name__ == "__main__":
    unittest.main()
