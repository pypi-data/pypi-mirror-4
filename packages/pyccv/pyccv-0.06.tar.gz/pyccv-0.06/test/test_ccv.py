# -*- coding: utf-8 -*-
import Image
import unittest
import pyccv

class TestCcv(unittest.TestCase):
    def test_ccv(self):
        img = Image.open("./test/test.bmp")
        ccv = pyccv.calc_ccv(img,240,25)
        print ccv

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TestCcv))
  return suite
