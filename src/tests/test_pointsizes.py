# Allow direct execution
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from lib.pointsizes import Pointsizes

class SheetTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test(self):
        self.assertEquals(Pointsizes.min(), 1)
        self.assertEquals(Pointsizes.max(), 23)
        self.assertEquals(Pointsizes.normal(), 12)
        self.assertEquals(Pointsizes.percentage(12), 100)
        self.assertEquals(Pointsizes.toFontSize(12), 12)
        self.assertEquals(Pointsizes.toFontSize(50), 72)
        self.assertEquals(Pointsizes.toFontSize(-2), 1)
        self.assertEquals(Pointsizes.toFontSize(16), 20)
        self.assertEquals(Pointsizes.zoom(11, +2), 13)
        self.assertEquals(Pointsizes.zoom(11, +20), 23)
        self.assertEquals(Pointsizes.zoom(11, -2), 9)
        self.assertEquals(Pointsizes.zoom(11, -20), 1)
        self.assertEquals(Pointsizes.toPointSize(11), 11)
        self.assertEquals(Pointsizes.toPointSize(100), 23)
        self.assertEquals(Pointsizes.toPointSize(0), 1)
        self.assertEquals(Pointsizes.toPointSize(14), 13)


if __name__ == '__main__':
    unittest.main()
