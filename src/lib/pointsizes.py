from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Standard font point sizes
StandardPointSizes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]

class Pointsizes(object):

    @staticmethod
    def min():
        return 1

    @staticmethod
    def max():
        return len(StandardPointSizes)

    @staticmethod
    def normal():
        fontSize = QFont().pointSize()
        return Pointsizes.toPointSize(fontSize)

    @staticmethod
    def percentage(value):
        fontSize = Pointsizes.toFontSize(value)
        normalFontSize = Pointsizes.toFontSize(Pointsizes.normal())
        return (fontSize * 100) / normalFontSize

    @staticmethod
    def zoom(value, rate):
        value = value + rate
        min = Pointsizes.min()
        max = Pointsizes.max()
        if value < min:
            value = min
        if value > max:
            value = max
        return value

    @staticmethod
    def toFontSize(value):
        value = Pointsizes.zoom(value, 0)
        return StandardPointSizes[value - 1]

    @staticmethod
    def toPointSize(value):
        if value in StandardPointSizes:
            return StandardPointSizes.index(value) + 1
        else:
            if value < min(StandardPointSizes):
                return Pointsizes.min()
            elif value > max(StandardPointSizes):
                return Pointsizes.max()
            else:
                for fontSize in StandardPointSizes:
                    if fontSize > value:
                        return StandardPointSizes.index(fontSize) + 1
                return Pointsizes.normal()
