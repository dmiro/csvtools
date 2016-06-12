# Allow direct execution
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest import TestCase
from lib.pointsizes import Pointsizes

class SheetTestCase(TestCase):

    def setUp(self):
        pass

    def test_1(self):
        self.assertEquals(Pointsizes.min(), 0)
        self.assertEquals(Pointsizes.max(), 22)
        self.assertEquals(Pointsizes.normal(), 11)
        self.assertEquals(Pointsizes.percentage(11), 100)
        self.assertEquals(Pointsizes.toFontSize(11), 12)
        self.assertEquals(Pointsizes.toFontSize(50), 72)
        self.assertEquals(Pointsizes.toFontSize(-2), 1)
        self.assertEquals(Pointsizes.toFontSize(15), 20)
        self.assertEquals(Pointsizes.zoom(11, +2), 13)
        self.assertEquals(Pointsizes.zoom(11, +20), 22)
        self.assertEquals(Pointsizes.zoom(11, -2), 9)
        self.assertEquals(Pointsizes.zoom(11, -20), 0)
        self.assertEquals(Pointsizes.toPointSize(12), 11)
        self.assertEquals(Pointsizes.toPointSize(100), 22)
        self.assertEquals(Pointsizes.toPointSize(0), 0)
        self.assertEquals(Pointsizes.toPointSize(15), 13)


if __name__ == '__main__':
    unittest.main()
