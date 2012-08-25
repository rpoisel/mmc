#!/usr/bin/env python

import unittest

from mm_context import CFileCarver


class CTestFloppyImage(unittest.TestCase):
    def setUp(self):
        self.verbose = None
        self.offset = 0
        self.imagefile = '/tmp/practical.floppy.dd'
        self.incrementsize = 4096
        self.fragmentsize = 4096
        self.preprocess = False
        self.output = '/tmp/clever-output'

    def test_floppy_image(self):
        lContext = CFileCarver()
        lContext.run(self)

class CTestFeasibilityImage4096(unittest.TestCase):
    def setUp(self):
        self.verbose = None
        self.offset = 0
        self.imagefile = '/home/rpoisel/nosvn/feasibility_images/image_06.img'
        self.incrementsize = 4096
        self.fragmentsize = 4096
        self.preprocess = False
        self.output = '/tmp/clever-output'

    def test_feasibility_image(self):
        lContext = CFileCarver()
        lContext.run(self) 

class CTestFeasibilityImage512(unittest.TestCase):
    def setUp(self):
        self.verbose = None
        self.offset = 0
        self.imagefile = '/home/rpoisel/nosvn/feasibility_images/image_06.img'
        self.incrementsize = 512
        self.fragmentsize = 512
        self.preprocess = False
        self.output = '/tmp/clever-output'

    def test_feasibility_image(self):
        lContext = CFileCarver()
        lContext.run(self) 

if __name__ == "__main__":
    lSuite = unittest.TestLoader().loadTestsFromTestCase(CTestFloppyImage)
    unittest.TextTestRunner(verbosity=2, descriptions=2).run(lSuite)
    lSuite = unittest.TestLoader().loadTestsFromTestCase(CTestFeasibilityImage4096)
    unittest.TextTestRunner(verbosity=2, descriptions=2).run(lSuite)
    lSuite = unittest.TestLoader().loadTestsFromTestCase(CTestFeasibilityImage512)
    unittest.TextTestRunner(verbosity=2, descriptions=2).run(lSuite)
