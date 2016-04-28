from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import xlrd
import csv


class SimpleNamespace:
    """backport of SimpleNamespace Python 3.3 to simulate an anonymous class
    https://docs.python.org/3/library/types.html#types.SimpleNamespace
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

def waiting(function):
    """decorator function. Show hour glass while waiting end method"""
    def new_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
    return new_function

def bestUnitSize(bytes_size):
    """Get a size in bytes & convert it to the best IEC prefix for readability.
    Return a dictionary with three pair of keys/values:
    "s" -- (float) Size of path converted to the best unit for easy read
    "u" -- (str) The prefix (IEC) for s (from bytes(2^0) to YiB(2^80))
    "b" -- (int / long) The original size in bytes
    http://joedicastro.com/conocer-el-tamano-de-un-directorio-con-python.html
    """
    for exp in range(0, 90 , 10):
        bu_size = abs(bytes_size) / pow(2.0, exp)
        if int(bu_size) < 2 ** 10:
            unit = {0:"bytes", 10:"KiB", 20:"MiB", 30:"GiB", 40:"TiB", 50:"PiB",
                    60:"EiB", 70:"ZiB", 80:"YiB"}[exp]
            break
    return {"s":bu_size, "u":unit, "b":bytes_size}

def get_size(filename):
    """Get the file size in format string"""
    bytesize = os.lstat(filename).st_size
    size = bestUnitSize(bytesize)
    return "{0:.2f} {1}".format(size['s'], size['u'])

def get_excel_sheets(filename):
    sh = []
    wb = xlrd.open_workbook(filename)
    for sheet in wb.sheets():
        sh.append([sheet.number, sheet.name, sheet.nrows, sheet.ncols])
    return sh

def QStringToUnicode(qstring):
    return unicode(qstring.toUtf8(), encoding="UTF-8")

def QStringListToUnicode(qstringlist):
    return [QStringToUnicode(value) for value in qstringlist]

def QStringMatrixToUnicode(qstringmatrix):
    return [[QStringToUnicode(value) for value in row] for row in qstringmatrix]

# por ahora sin uso
#def isSelectedRectangle(selectedIndexes):
    #"""determine if list-of-QModelIndex selection is a rectangular area"""
    #if len(selectedIndexes):
        #minIndex = selectedIndexes[0]
        #maxIndex = selectedIndexes[len(selectedIndexes)-1]
        #numColumns = maxIndex.column() - minIndex.column() + 1
        #numRows = maxIndex.row() - minIndex.row() + 1
        #numItems = numColumns * numRows

        #if numItems == len(selectedIndexes):
            #for item in selectedIndexes:
                #innerCell = item.column() >= minIndex.column() and item.row() >= minIndex.row() and item.column() <= maxIndex.column() and item.row() <= maxIndex.row()
                #if not innerCell:
                    #return False
            #return True
    #return False




