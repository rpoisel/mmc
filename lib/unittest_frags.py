#!/usr/bin/env python

import unittest

import frags


class CTestFrags(unittest.TestCase):
    def setUp(self):
        self.__mNumHeaders = 1000
        self.__mNumIter = 2

    def test_frags_and_headers(self):
        lFrags = frags.CFrags()
        for lIter in xrange(self.__mNumIter):
            for lOffset in xrange(self.__mNumHeaders):
                lFrags.addHeader(lOffset)
        self.assertEquals(len(lFrags.getHeaders()), len(lFrags.getBlocks()))
        self.assertEquals(lFrags.getHeaders()[20], lFrags.getBlocks()[20])

if __name__ == "__main__":
    lSuite = unittest.TestLoader().loadTestsFromTestCase(CTestFrags)
    unittest.TextTestRunner(verbosity=2, descriptions=2).run(lSuite)
