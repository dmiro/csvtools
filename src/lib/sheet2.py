import copy
import numpy as np

class Sheet(object):

    #
    # init
    #

    def __init__(self, valueClass, arrayData=[]):
        self.__valueClass = valueClass
        self.setArrayData(arrayData)
        super(Sheet, self).__init__()

    #
    # private
    #

    def __expand(self, row, column):
        if self.__arrayData.size == 0:
            self.__arrayData = np.empty([row+1, column+1], dtype=object)
        else:
            # rows
            missingRows = row - self.rowCount() + 1
            if missingRows > 0:
                emptyRows = np.empty([missingRows, self.columnCount()], dtype=object)
                self.__arrayData = np.vstack((self.__arrayData, emptyRows))
            # columns
            missingColumns = column - self.columnCount() + 1
            if missingColumns > 0:
                emptyColumns = np.empty([self.rowCount(), missingColumns], dtype=object)
                self.__arrayData = np.hstack((self.__arrayData, emptyColumns))

    def __constraint(self):
        # rows
        while self.rowCount() > 0 and \
              all(item in (None, '') for item in self.__arrayData[-1]):
                self.__arrayData = np.delete(self.__arrayData, -1, 0)
        # columns
        while self.columnCount() > 0 and \
              all(item in (None, '') for item in self.__arrayData[:, -1]):
                self.__arrayData = np.delete(self.__arrayData, -1, 1)

    #
    # public
    #

    def arrayData(self):
        return self.__arrayData.tolist()

    def setArrayData(self, arrayData):
        if arrayData:
            maxColumnSize = max(len(row) for row in arrayData)   
            for row in arrayData:
                missingColumns = maxColumnSize - len(row)
                if missingColumns > 0:
                    row.extend([self.__valueClass() for _ in xrange(missingColumns)])
        self.__arrayData = np.array(arrayData, dtype=object)

    def rowCount(self):
        """get row count"""
        return self.__arrayData.shape[0]

    def columnCount(self):
        """get column count"""
        shape = self.__arrayData.shape
        if len(shape) == 2:
            return shape[1]
        else:
            return 0

    def value(self, row, column):
        """get cell value"""
        if self.rowCount() > row:
            if self.columnCount() > column:
                if self.__arrayData[row, column]:
                    return self.__arrayData[row, column]
        return self.__valueClass()

    def setValue(self, row, column, cellValue):
        # check
        if row < 0:
            raise IndexError('row index must be positive')
        if column < 0:
            raise IndexError('column index must be positive')
        if not isinstance(cellValue, self.__valueClass):
            raise TypeError('cellValue != ' + self.__valueClass.__class__.__name__)
        # expand rows & columns
        self.__expand(row, column)
        # set value
        self.__arrayData[row, column] = cellValue
        # constraint rows & columns
        self.__constraint()

    def removeColumns(self, startColumn, endColumn):
        # check
        if startColumn < 0:
            raise IndexError('column index must be positive')
        if endColumn < 0:
            raise IndexError('column index must be positive')
        if startColumn >= self.columnCount():
            raise IndexError('column index out of range')
        if endColumn >= self.columnCount():
            raise IndexError('column index out of range')
        if endColumn < startColumn:
            raise IndexError('startColumn must be smaller than endColumn')
        # remove
        self.__arrayData = np.delete(self.__arrayData, xrange(startColumn, endColumn+1), 1)
        # constraint rows & columns
        self.__constraint()

    def removeColumn(self, column):
        self.removeColumns(column, column)

    def removeRows(self, startRow, endRow):
        # check
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if endRow < 0:
            raise IndexError('endRow must be positive')
        if startRow >= self.rowCount():
            raise IndexError('startRow out of range')
        if endRow >= self.rowCount():
            raise IndexError('row index out of range')
        if endRow < startRow:
            raise IndexError('startRow must be smaller than endRow')
        # remove
        self.__arrayData = np.delete(self.__arrayData, xrange(startRow, endRow+1), 0)
        # constraint rows & columns
        self.__constraint()

    def removeRow(self, row):
        self.removeRows(row, row)

    def insertRows(self, startRow, rows):
        # check
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if rows:
            # expand rows
            maxColumnSize = max(len(row) for row in rows) 
            self.__expand(startRow, maxColumnSize-1)
            # insert
            self.__arrayData = np.insert(self.__arrayData, startRow, rows, axis=0)
            # constraint rows & columns
            self.__constraint()

    def insertColumns(self, startColumn, columns):
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if columns:
            # expand rows
            maxRowSize = max(len(column) for column in columns) 
            self.__expand(maxRowSize-1, startColumn)
            # insert
            print 'aa', columns
            print 'bb', self.arrayData()
            self.__arrayData = np.insert(self.__arrayData, startColumn, columns, axis=1)
            # constraint rows & columns
            self.__constraint()

#
# test
#

if __name__ == '__main__':

    import unittest
    from unittest import TestCase
    from PyQt4.QtCore import *

    class SheetTestCase(TestCase):

        def setUp(self):
            pass

        def test_init(self):
            sh = Sheet(valueClass=QString)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)

        def test_dimensions(self):
            sh = Sheet(QString, [['1','2']])
            self.assertEqual(sh.rowCount(), 1)
            self.assertEqual(sh.columnCount(), 2)
            #
            sh = Sheet(QString, [['1','2'], ['3','4']])
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 2)
            #
            sh = Sheet(QString, [['1','2'], ['3','4','5']])
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)

        def test_setvalue_str_class(self):
            sh = Sheet(valueClass=str)
            sh.setValue(3, 3, 'cell 3-3')
            self.assertEqual(sh.value(2,2), '')
            self.assertEqual(sh.value(3,3), 'cell 3-3')
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 4)
            #
            sh.setValue(3, 3, 'cell 3-3 new')
            self.assertEqual(sh.value(3,3), 'cell 3-3 new')
            #
            sh.setValue(3, 3, '')
            self.assertEqual(sh.value(3,3), '')
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)

        def test_setvalue(self):
            sh = Sheet(valueClass=QString)
            sh.setValue(3, 3, QString('cell 3-3'))
            self.assertEqual(sh.value(2,2), '')
            self.assertEqual(sh.value(3,3), 'cell 3-3')
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 4)
            #
            sh.setValue(3, 3, QString('cell 3-3 new'))
            self.assertEqual(sh.value(3,3), 'cell 3-3 new')
            #
            with self.assertRaises(IndexError):
                sh.setValue(-1, 2, QString('cell 3-3'))
            with self.assertRaises(IndexError):
                sh.setValue(1, -2, QString('cell 3-3'))
            with self.assertRaises(IndexError):
                sh.setValue(-1, -2, QString('cell 3-3'))
            #
            sh.setValue(3, 3, QString(''))
            self.assertEqual(sh.value(3,3), '')
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)

        def test_typeerror(self):
            sh = Sheet(valueClass=QString)
            with self.assertRaises(TypeError):
                sh.setValue(3, 3, 1000)

        def test_emptySetArrayData(self):
            arrayData = []
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            #
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            self.assertEqual(sh.value(300,300), '')

        def test_setArrayData(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['', QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            #
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '2-1')
            self.assertEqual(sh.value(2,2), '2-2')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '3-1')
            self.assertEqual(sh.value(3,2), '')
            self.assertEqual(sh.value(300,300), '')

        def test_remove_column(self):
            sh = Sheet(valueClass=QString)
            #
            # test 1
            #
            sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
            sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeColumn(0)
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 2)
            #
            sh.removeColumn(0)
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 1)
            #
            sh.removeColumn(0)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 2
            #
            sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
            sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeColumn(2)
            self.assertEqual(sh.rowCount(), 1)
            self.assertEqual(sh.columnCount(), 2)
            #
            with self.assertRaises(IndexError):
                sh.removeColumn(2)
            #
            sh.removeColumn(1)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            with self.assertRaises(IndexError):
                sh.removeColumn(0)

        def test_remove_columns(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeColumns(1, 2)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 1)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '')
            #
            # test 2: negative indexes is not allowed
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeColumns(-2, -1)
            #
            # test 3: empty all
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeColumns(0, 2)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,1), '')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(3,0), '')
            self.assertEqual(sh.value(3,1), '')

        def test_remove_row(self):
            sh = Sheet(valueClass=QString)
            #
            # test 1
            #
            sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
            sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeRow(0)
            self.assertEqual(sh.rowCount(), 1)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeRow(0)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 2
            #
            sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
            sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeRow(1)
            self.assertEqual(sh.rowCount(), 1)
            self.assertEqual(sh.columnCount(), 2)
            #
            with self.assertRaises(IndexError):
                sh.removeRow(1)
            #
            sh.removeRow(0)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 3
            #
            sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
            sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeRow(-1)

        def test_remove_rows(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['', QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeRows(1, 2)
            self.assertEqual(sh.rowCount(), 2)
            self.assertEqual(sh.columnCount(), 2)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(1,0), '3-0')
            self.assertEqual(sh.value(1,1), '3-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            #
            # test 2
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeRows(-2, -1)
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.removeRows(0, 3)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,1), '')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')

        def test_insert_columns(self):
            arrayData = [['1','2'],
                         ['a','e'],
                         ['6','7'],
                         ['11','12']]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(0, ['a','b','c','d'])
            self.assertEqual(sh.arrayData(), [['a','1','2'], ['b','a','e'], ['c','6','7'], ['d','11','12']])
            #
            # test 2
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(2, [['a','b','c','d'], ['a','b','c','d']])
            self.assertEqual(sh.arrayData(), [['1','2','a','a'], ['a','e','b','b'], ['6','7','c','c'], ['11','12','d','d']])
##            #
##            # test 3
##            #
##            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
##            sh.insertRows(0, arrayData[0:2])
##            self.assertEqual(sh.arrayData(), [['1','2'],['a','e'],['1','2'], ['a','e'], ['6','7'], ['11','12']])
##            #
##            # test 4
##            #
##            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
##            sh.insertRows(4, arrayData[0:2])
##            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2'], ['a','e']])
##            #
##            # test 5
##            #
##            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
##            sh.insertRows(6, arrayData[0:2])
##            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'],[],[],['1','2'], ['a','e']])

        def test_insert_rows(self):
            arrayData = [['1','2'],
                         ['a','e'],
                         ['6','7'],
                         ['11','12']]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(0, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2'], ['1','2',], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 2
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2']])
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(0, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],['a','e'],['1','2'], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 4
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2'], ['a','e']])
            #
            # test 5
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(6, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'],[None, None],[None, None],['1','2'], ['a','e']])


    unittest.main()

