import copy
import numpy as np

class Sheet(object):

    #
    # init
    #

    def __init__(self, valueClass, arrayData=None):
        self.__valueClass = valueClass
        if arrayData:
            self.setArrayData(arrayData)
        else:
            self.setArrayData([])
        super(Sheet, self).__init__()

    #
    # private
    #

    def __expandColumnsArray(self, arrayData, column):
        """expand up column specified in a python array """
        if arrayData:
            # columns
            for row in arrayData:
                missingColumns = column - len(row) + 1
                if missingColumns > 0:
                    row.extend([None for _ in xrange(missingColumns)])
        return arrayData

    def __expand(self, row, column):
        """expand up row and column specified in a numpy array """
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
        """delete rows and columns to the right without values"""
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
        """get array"""
        # numpy array -> array
        return self.__arrayData.tolist()

    def setArrayData(self, arrayData):
        """set array"""
        # all rows must have the same number of columns
        if arrayData:
            maxColumnSize = max(len(row) for row in arrayData)
            for row in arrayData:
                missingColumns = maxColumnSize - len(row)
                if missingColumns > 0:
                    row.extend([None for _ in xrange(missingColumns)])
                    #row.extend([self.__valueClass() for _ in xrange(missingColumns)])
        # array -> numpy array & delete dimensions with a single element
        self.__arrayData = np.array(arrayData, dtype=object).squeeze()
        # obtain column dim if it's undefined
        if len(self.__arrayData.shape) == 1:
            if self.__arrayData.shape[0] > 0:
                self.__arrayData = self.__arrayData.reshape(len(arrayData), -1)

    def rowCount(self):
        """get row count"""
        return self.__arrayData.shape[0]

    def columnCount(self):
        """get column count"""
        if len(self.__arrayData.shape) > 1:
            return self.__arrayData.shape[1]
        return 0

    def isEmpty(self):
        return self.__arrayData.size == 0

    def value(self, row, column):
        """get cell value"""
        if self.rowCount() > row:
            if self.columnCount() > column:
                if self.__arrayData[row, column]:
                    return self.__arrayData[row, column]
        return self.__valueClass()

    def setValue(self, row, column, cellValue):
        """set cell value"""
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
            # expand columns array
            maxColumnSize = max(max(len(row) for row in rows), self.columnCount())
            rows = self.__expandColumnsArray(rows, maxColumnSize-1)
            # insert rows
            self.insertArrayInRows(startRow=startRow,
                                   startColumn=0,
                                   array=rows)

    def insertEmptyRows(self, startRow, count):
        # check
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        # insert
        if self.columnCount() > 0:
            self.insertEmptyCellsInRows(startRow=startRow,
                                        startColumn=0,
                                        dimRows=count,
                                        dimColumns=self.columnCount())

    def insertEmptyRow(self, row):
        self.insertEmptyRows(row, 1)

    def insertColumns(self, startColumn, columns):
        # check
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if columns:
            maxRowSize = max(max(len(column) for column in columns), self.rowCount())
            # expand columns array
            columns = self.__expandColumnsArray(columns, maxRowSize-1)
            # expand columns numpy array
            self.__expand(maxRowSize-1, startColumn)
            # insert
            self.__arrayData = np.insert(self.__arrayData, startColumn, columns, axis=1)
            # constraint rows & columns
            self.__constraint()

    def insertEmptyColumns(self, startColumn, count):
        # check
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        # insert
        columns = [[] for _ in xrange(count)]
        self.insertColumns(startColumn, columns)

    def insertEmptyColumn(self, startColumn):
        self.insertEmptyColumns(startColumn, 1)

    def moveRows(self, originRow, count, destinationRow):
        # checks
        if originRow < 0:
            raise IndexError('originRow must be positive')
        if destinationRow < 0:
            raise IndexError('destinationRow must be positive')
        if count < 1:
            raise IndexError('count must be higher than zero')
        if destinationRow in range(originRow, originRow+count):
            raise IndexError('destinationRow cannot be within place to move')
        # calculate source rows empty and missing
        if originRow > self.rowCount():
            dataRows = 0
            missingRows = count
        else:
            dataRows = min(self.rowCount() - originRow, count)
            missingRows = count - dataRows
        # move
        self.insertRows(destinationRow,
                        self.__arrayData[originRow: originRow + dataRows].tolist() + [[] for _ in xrange(missingRows)])
        if dataRows > 0:
            if destinationRow < originRow:
                self.removeRows(originRow + count,
                                originRow + count + dataRows - 1)
            else:
                self.removeRows(originRow,
                                originRow + dataRows - 1)

    def moveRow(self, originRow, destinationRow):
        self.moveRows(originRow, 1, destinationRow)

    def moveColumns(self, originColumn, count, destinationColumn):
        # checks
        if originColumn < 0:
            raise IndexError('originColumn must be positive')
        if destinationColumn < 0:
            raise IndexError('destinationColumn must be positive')
        if count < 1:
            raise IndexError('count must be higher than zero')
        if destinationColumn in range(originColumn, originColumn+count):
            raise IndexError('destinationColumn cannot be within place to move')
        # calculate source rows empty and missing
        if originColumn > self.rowCount():
            dataColumns = 0
            missingColumns = count
        else:
            dataColumns = min(self.columnCount() - originColumn, count)
            missingColumns = count - dataColumns
        # move
        self.insertColumns(destinationColumn,
                           self.__arrayData[:, originColumn: originColumn + dataColumns].transpose().tolist())
        self.insertEmptyColumns(destinationColumn + dataColumns, missingColumns)
        if dataColumns > 0:
            if destinationColumn < originColumn:
                self.removeColumns(originColumn + count,
                                   originColumn + count + dataColumns - 1)
            else:
                self.removeColumns(originColumn,
                                   originColumn + dataColumns - 1)

    def moveColumn(self, originColumn, destinationColumn):
        self.moveColumns(originColumn, 1, destinationColumn)

    def insertArrayInRows(self, startRow, startColumn, array):
        """ example

          arrayData =                startRow=1      sourceArray =
          [[11 12 13 14 15 16]       startColumn=1     [[996 997]
           [17 18 19 20 21 22]                          [998 999]]
           [23 24 25 26 27 28]
           [29 30 31 32 33 34]]

          result =
           [[11 12 13 14 15 16]
            [17 996 997 20 21 22]
            [23 998 999 26 27 28]
            [29 18 19 32 33 34]
            [None 24 25 None None None]
            [None 30 31 None None None]]
        """
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        sourceArray = np.array(array, dtype=object)
        if sourceArray.size > 0:
            # get source shapes
            sourceRows = sourceArray.shape[0]
            sourceColumns = sourceArray.shape[1]
            if not self.isEmpty():
                # get destination shapes
                destRows = self.rowCount()
                destColumns = self.columnCount()
                # add empty rows at last
                missingRows = max(startRow - destRows, 0) + sourceRows
                emptyRows = np.empty([missingRows, destColumns], dtype=object)
                self.__arrayData = np.concatenate((self.__arrayData, emptyRows), axis=0)
                # if missing columns, add empty columns at right
                missingColumns = startColumn + sourceColumns - self.columnCount()
                if missingColumns > 0:
                    emptyColumns = np.empty([self.__arrayData.shape[0], missingColumns], dtype=object)
                    self.__arrayData = np.concatenate((self.__arrayData, emptyColumns), axis=1)
                # copy slice array to new position
                self.__arrayData[startRow+sourceRows:destRows+sourceRows, startColumn:startColumn+sourceColumns] = \
                                 self.__arrayData[startRow:destRows, startColumn:startColumn+sourceColumns]
            else:
                self.__arrayData = np.empty([startRow+sourceRows, startColumn+sourceColumns], dtype=object)
            # set values
            self.__arrayData[startRow:startRow+sourceRows, startColumn:startColumn+sourceColumns] = sourceArray
            # constraint rows & columns
            self.__constraint()

    def insertEmptyCellsInRows(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        sourceArray = np.empty([dimRows,dimColumns], dtype=object)
        return self.insertArrayInRows(startRow, startColumn, sourceArray)


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
            sh.insertColumns(0, [['a','b','c','d']])
            self.assertEqual(sh.arrayData(), [['a','1','2'],
                                              ['b','a','e'],
                                              ['c','6','7'],
                                              ['d','11','12']])
            #
            # test 2
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(2, [['a','b','c','d'], ['a','b','c','d']])
            self.assertEqual(sh.arrayData(), [['1','2','a','a'],
                                              ['a','e','b','b'],
                                              ['6','7','c','c'],
                                              ['11','12','d','d']])
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(4, [['a','b','c','d']])
            self.assertEqual(sh.arrayData(), [['1','2',None, None,'a'],
                                              ['a','e',None, None,'b'],
                                              ['6','7',None, None,'c'],
                                              ['11','12',None, None,'d']])
            #
            # test 5
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(0, [['a','b','c']])
            self.assertEqual(sh.arrayData(), [['a','1','2'],
                                              ['b','a','e'],
                                              ['c','6','7'],
                                              [None,'11','12']])
            #
            # test 6
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertColumns(0, [['a'],['a','b'], ['a','b','c','d','e']])
            self.assertEqual(sh.arrayData(), [['a','a','a','1','2'],
                                              [None, 'b','b','a','e'],
                                              [None, None,'c','6','7'],
                                              [None, None,'d','11','12'],
                                              [None, None,'e',None,None]])

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
            self.assertEqual(sh.arrayData(), [['1','2'],
                                              ['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12']])
            #
            # test 2
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12'],
                                              ['1','2']])
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(0, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],
                                              ['a','e'],
                                              ['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12']])
            #
            # test 4
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12'],
                                              ['1','2'],
                                              ['a','e']])
            #
            # test 5
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(6, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12'],
                                              [None, None],
                                              [None, None],
                                              ['1','2'],
                                              ['a','e']])
            #
            # test 6
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(0, [['1']])
            self.assertEqual(sh.arrayData(), [['1',None],
                                              ['1','2'],
                                              ['a','e'],
                                              ['6','7'],
                                              ['11','12']])
            #
            # test 7
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertRows(0, [['1'],
                              ['2','3'],
                              ['4'],
                              ['5','6','7']])
            self.assertEqual(sh.arrayData(), [['1',None, None],
                                              ['2','3',None],
                                              ['4',None,None],
                                              ['5','6','7'],
                                              ['1','2',None],
                                              ['a','e',None],
                                              ['6','7',None],
                                              ['11','12',None]])

        def test_insert_empty_row(self):
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
            sh.insertEmptyRow(2)
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(2,3), '')
            self.assertEqual(sh.value(3,0), '')
            self.assertEqual(sh.value(3,1), '2-1')
            self.assertEqual(sh.value(3,2), '2-2')
            self.assertEqual(sh.value(4,0), '3-0')
            self.assertEqual(sh.value(4,1), '3-1')
            #
            # test 2: insert row in tenth position it has no effect
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.insertEmptyRow(10)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '2-1')
            self.assertEqual(sh.value(2,2), '2-2')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '3-1')
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.insertEmptyRow(0)
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,1), '')
            self.assertEqual(sh.value(2,0), '1-0')
            self.assertEqual(sh.value(2,1), '1-1')
            self.assertEqual(sh.value(3,0), '')
            self.assertEqual(sh.value(3,1), '2-1')
            self.assertEqual(sh.value(3,2), '2-2')
            self.assertEqual(sh.value(4,0), '3-0')
            self.assertEqual(sh.value(4,1), '3-1')
            #
            # test 4
            #
            sh = Sheet(valueClass=QString)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            sh.insertEmptyRow(2)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)

        def test_insert_empty_rows(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1: insert three rows to the middle
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.insertEmptyRows(2, 3)
            self.assertEqual(sh.rowCount(), 7)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(2,3), '')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(2,3), '')
            self.assertEqual(sh.value(4,0), '')
            self.assertEqual(sh.value(4,1), '')
            self.assertEqual(sh.value(4,3), '')
            self.assertEqual(sh.value(5,0), '')
            self.assertEqual(sh.value(5,1), '2-1')
            self.assertEqual(sh.value(5,2), '2-2')
            self.assertEqual(sh.value(6,0), '3-0')
            self.assertEqual(sh.value(6,1), '3-1')
            #
            # test 2: insert three rows to row tenth position it has no effect
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.insertEmptyRows(10, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '2-1')
            self.assertEqual(sh.value(2,2), '2-2')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '3-1')
            #
            # test 3: insert three rows to the top
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            sh.insertEmptyRows(0, 3)
            self.assertEqual(sh.rowCount(), 7)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,1), '')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(3,0), '')
            self.assertEqual(sh.value(3,1), '')
            self.assertEqual(sh.value(4,0), '1-0')
            self.assertEqual(sh.value(4,1), '1-1')
            self.assertEqual(sh.value(5,0), '')
            self.assertEqual(sh.value(5,1), '2-1')
            self.assertEqual(sh.value(5,2), '2-2')
            self.assertEqual(sh.value(6,0), '3-0')
            self.assertEqual(sh.value(6,1), '3-1')
            #
            # test 4: insert rows in empty sheet results a empty sheet
            #
            sh = Sheet(valueClass=QString)
            sh.insertEmptyRows(2, 10)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 5
            #
            sh = Sheet(valueClass=QString)
            sh.insertEmptyRows(2, 0)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 6: count must be greater or equal than zero
            #
            sh = Sheet(valueClass=QString)
            with self.assertRaises(IndexError):
                sh.insertEmptyRows(2, -1)

        def test_insert_empty_column(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1: insert one column to the middle
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumn(2)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 4)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '2-1')
            self.assertEqual(sh.value(2,2), '')
            self.assertEqual(sh.value(2,3), '2-2')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '3-1')
            #
            # test 2: insert column in tenth position it has not effect.
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumn(10)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(1,0), '1-0')
            self.assertEqual(sh.value(1,1), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '2-1')
            self.assertEqual(sh.value(2,2), '2-2')
            self.assertEqual(sh.value(3,0), '3-0')
            self.assertEqual(sh.value(3,1), '3-1')
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumn(0)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 4)
            self.assertEqual(sh.value(0,0), '')
            self.assertEqual(sh.value(0,1), '')
            self.assertEqual(sh.value(0,2), '')
            self.assertEqual(sh.value(1,0), '')
            self.assertEqual(sh.value(1,1), '1-0')
            self.assertEqual(sh.value(1,2), '1-1')
            self.assertEqual(sh.value(2,0), '')
            self.assertEqual(sh.value(2,1), '')
            self.assertEqual(sh.value(2,2), '2-1')
            self.assertEqual(sh.value(2,3), '2-2')
            self.assertEqual(sh.value(3,0), '')
            self.assertEqual(sh.value(3,1), '3-0')
            self.assertEqual(sh.value(3,2), '3-1')
            #
            # test 4
            #
            sh = Sheet(valueClass=QString)
            sh.insertEmptyColumn(2)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 5
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy([['1','2']]))
            sh.insertEmptyColumn(1)
            self.assertEqual(sh.arrayData(), [['1',None,'2']])

        def test_insert_empty_columns(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumns(2, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 2: insert three columns to column tenth position it has no effect
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumns(10, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            # test 3: insert three columns to the top
            #
            sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyColumns(0, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 4: insert columns in empty sheet results a empty sheet
            #
            sh = Sheet(valueClass=QString)
            sh.insertEmptyColumns(2, 10)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 5
            #
            sh = Sheet(valueClass=QString)
            sh.insertEmptyColumns(2, 0)
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            #
            # test 6: countColumn must be greater or equal than zero
            #
            sh = Sheet(valueClass=QString)
            with self.assertRaises(IndexError):
                sh.insertEmptyColumns(2, -1)

        def test_move_row(self):
            arrayData = [['1','2','3','4','5'],
                         ['a','e','i','o','u'],
                         ['6','7','8','9','10'],
                         ['11','12','13','14','15']]
            #
            # test 1
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRow(0, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'],
                                              ['1','2','3','4','5'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            #
            # test 2
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRow(2, 5)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['11','12','13','14','15'],
                                              [None, None, None, None, None],
                                              ['6','7','8','9','10']])

        def test_move_rows(self):
            arrayData = [['1','2','3','4','5'],
                         ['a','e','i','o','u'],
                         ['6','7','8','9','10'],
                         ['11','12','13','14','15']]
            #
            # test 1
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'],
                                              ['1','2','3','4','5'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 2
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(0, 2, 3)
            self.assertEqual(sh.arrayData(), [['6','7','8','9','10'],
                                              ['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 3
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(0, 2, 2)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 4
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(3, 1, 0)
            self.assertEqual(sh.arrayData(), [['11','12','13','14','15'],
                                              ['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 5
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(3, 1, 6)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              [None,None,None,None,None],
                                              [None,None,None,None,None],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 6
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              [None,None,None,None,None],
                                              [None,None,None,None,None],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 7
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(3, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              ['11','12','13','14','15'],
                                              [None,None,None,None,None],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 8
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(5, 1, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              [None,None,None,None,None],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 9
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 0)
            self.assertEqual(sh.arrayData(), [[None,None,None,None,None],
                                              [None,None,None,None,None],
                                              ['1', '2', '3', '4', '5'],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 10
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 4)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 11
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(50, 20, 40)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 12
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 5)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15'],
                                              [None,None,None,None,None],
                                              ['1', '2', '3', '4', '5']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 13
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 7)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              ['11','12','13','14','15'],
                                              [None,None,None,None,None],
                                              [None,None,None,None,None],
                                              [None,None,None,None,None],
                                              ['1', '2', '3', '4', '5']])
            self.assertEqual(sh.rowCount(), 7)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 14
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(7, 1, 3)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              [None, None, None, None, None],
                                              ['11', '12', '13', '14', '15']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 15
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveRows(7, 2, 3)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                              ['a', 'e', 'i', 'o', 'u'],
                                              ['6', '7', '8', '9', '10'],
                                              [None, None, None, None, None],
                                              [None, None, None, None, None],
                                              ['11', '12', '13', '14', '15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 16
            #
            sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            with self.assertRaises(IndexError):
                sh.moveRows(0, 2, 0)
            with self.assertRaises(IndexError):
                sh.moveRows(0, 2, 1)
            with self.assertRaises(IndexError):
                sh.moveRows(2, 1, 2)
            with self.assertRaises(IndexError):
                sh.moveRows(2, 2, 2)
            with self.assertRaises(IndexError):
                sh.moveRows(2, 2, 3)

        def test_move_columns(self):
            arrayData = [['1','2','3','4','5'],
                         ['a','e','i','o','u'],
                         ['6','7','8','9','10'],
                         ['11','12','13','14','15']]
            #
            # test 1
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(0, 1, 2)
            self.assertEqual(sh.arrayData(), [['2','1','3','4','5'],
                                              ['e','a','i','o','u'],
                                              ['7','6','8','9','10'],
                                              ['12','11','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 2
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(0, 2, 3)
            self.assertEqual(sh.arrayData(), [['3','1','2','4','5'],
                                              ['i','a','e','o','u'],
                                              ['8','6','7','9','10'],
                                              ['13','11','12','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 3
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(0, 1, 6)
            self.assertEqual(sh.arrayData(), [['2','3','4','5',None,'1'],
                                              ['e','i','o','u',None,'a'],
                                              ['7','8','9','10',None,'6'],
                                              ['12','13','14','15',None,'11']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 4
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(50, 2, 100)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 5
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(4, 1, 2)
            self.assertEqual(sh.arrayData(), [['1','2','5','3','4'],
                                              ['a','e','u','i','o'],
                                              ['6','7','10','8','9'],
                                              ['11','12','15','13','14']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 6
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(4, 3, 2)
            self.assertEqual(sh.arrayData(), [['1','2','5',None,None,'3','4'],
                                              ['a','e','u',None,None,'i','o'],
                                              ['6','7','10',None,None,'8','9'],
                                              ['11','12','15',None,None,'13','14']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 7)
            #
            # test 6
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.moveColumns(10, 3, 2)
            self.assertEqual(sh.arrayData(), [['1','2',None,None,None,'3','4','5'],
                                              ['a','e',None,None,None,'i','o','u'],
                                              ['6','7',None,None,None,'8','9','10'],
                                              ['11','12',None,None,None,'13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 8)

        def test_empty_cells_in_rows(self):
            arrayData = [['1100','1200','1300','1400','1500','1600'],
                         ['1700','1800','1900','2000','2100','2200'],
                         ['2300','2400','2500','2600','2700','2800'],
                         ['2900','3000','3100','3200','3300','3400']]
            #
            # test 1
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyCellsInRows(1, 1, 2, 2)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', None  , None  , '2000', '2100', '2200'],
                                             ['2300', None  , None  , '2600', '2700', '2800'],
                                             ['2900', '1800', '1900', '3200', '3300', '3400'],
                                             [None  , '2400', '2500', None  , None  , None],
                                             [None  , '3000', '3100', None  , None  , None]]);
            #
            # test 2
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyCellsInRows(2, 2, 2, 2)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', None , None   , '2700', '2800'],
                                             ['2900', '3000', None , None   , '3300', '3400'],
                                             [None  , None  , '2500', '2600', None  , None],
                                             [None  , None  , '3100', '3200', None  , None]]);
            #
            # test 3
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertEmptyCellsInRows(3, 3, 1, 3)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', '2500', '2600', '2700', '2800'],
                                             ['2900', '3000', '3100', None,    None,   None],
                                             [None,   None,   None,   '3200', '3300', '3400']]);
            #
            # test 4
            #
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            with self.assertRaises(IndexError):
                sh.insertEmptyCellsInRows(3, 3, 0, 0)
            #
            # test 5
            #
            sh=Sheet(valueClass=str)
            with self.assertRaises(IndexError):
                sh.insertEmptyCellsInRows(3, 3, 0, 0)

        def test_array_in_rows(self):
            arrayData = [['1100','1200','1300','1400','1500','1600'],
                         ['1700','1800','1900','2000','2100','2200'],
                         ['2300','2400','2500','2600','2700','2800'],
                         ['2900','3000','3100','3200','3300','3400']]
            #
            # test 1
            #
            sourceData = np.empty([2,2], dtype=object).tolist()
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(1, 1, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', None  , None  , '2000', '2100', '2200'],
                                             ['2300', None  , None  , '2600', '2700', '2800'],
                                             ['2900', '1800', '1900', '3200', '3300', '3400'],
                                             [None  , '2400', '2500', None  , None  , None],
                                             [None  , '3000', '3100', None  , None  , None]]);
            #
            # test 2
            #
            sourceData = np.empty([2,2], dtype=object).tolist()
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(2, 2, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', None , None   , '2700', '2800'],
                                             ['2900', '3000', None , None   , '3300', '3400'],
                                             [None  , None  , '2500', '2600', None  , None],
                                             [None  , None  , '3100', '3200', None  , None]]);
            #
            # test 3
            #
            sourceData = [['a','b','c']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(3, 3, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', '2500', '2600', '2700', '2800'],
                                             ['2900', '3000', '3100', 'a',    'b',    'c'],
                                             [None,   None,   None,   '3200', '3300', '3400']]);
            #
            # test 4
            #
            sourceData = [['a','b','c']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(3, 4, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None],
                                             ['2900', '3000', '3100', '3200', 'a',    'b',    'c'],
                                             [None,   None,   None,   None,   '3300', '3400', None]]);
            #
            # test 5
            #
            sourceData = [['a','b','c']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(3, 6, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                             ['2900', '3000', '3100', '3200', '3300', '3400', 'a',  'b',  'c']]);
            #
            # test 6
            #
            sourceData = [['a','b','c']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(4, 6, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                             ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                             [None,   None,   None,   None,   None,   None,   'a',  'b',  'c']]);
            #
            # test 7
            #
            sourceData = [['a','b','c']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(5, 6, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                             ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                             [None,   None,   None,   None,   None,   None,   None, None, None],
                                             [None,   None,   None,   None,   None,   None,   'a',  'b',  'c']]);
            #
            # test 8
            #
            sourceData = [['a','b','c'],['d','e','f']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(5, 6, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                             ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                             [None,   None,   None,   None,   None,   None,   None, None, None],
                                             [None,   None,   None,   None,   None,   None,   'a',  'b',  'c'],
                                             [None,   None,   None,   None,   None,   None,   'd',  'e',  'f']]);
            #
            # test 9
            #
            sourceData = [[]]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(5, 6, sourceData)
            self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', '2500', '2600', '2700', '2800'],
                                             ['2900', '3000', '3100', '3200', '3300', '3400']]);
            #
            # test 10
            #
            sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(0, 0, sourceData)
            self.assertEqual(sh.arrayData(),[['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['1100', '1200', '1300', '1400', '1500', '1600'],
                                             ['1700', '1800', '1900', '2000', '2100', '2200'],
                                             ['2300', '2400', '2500', '2600', '2700', '2800'],
                                             ['2900', '3000', '3100', '3200', '3300', '3400']]);
            #
            # test 11
            #
            sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
            sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
            sh.insertArrayInRows(0, 0, sourceData)
            self.assertEqual(sh.arrayData(),[['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             ['1100', '1200', '1300', '1400', '1500', '1600', None],
                                             ['1700', '1800', '1900', '2000', '2100', '2200', None],
                                             ['2300', '2400', '2500', '2600', '2700', '2800', None],
                                             ['2900', '3000', '3100', '3200', '3300', '3400', None]]);
            #
            # test 12
            #
            sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                          ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
            sh=Sheet(valueClass=str, arrayData=[])
            sh.insertArrayInRows(5, 2, sourceData)
            self.assertEqual(sh.arrayData(),[[None, None, None, None, None, None, None, None, None],
                                             [None, None, None, None, None, None, None, None, None],
                                             [None, None, None, None, None, None, None, None, None],
                                             [None, None, None, None, None, None, None, None, None],
                                             [None, None, None, None, None, None, None, None, None],
                                             [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                             [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]);


    unittest.main()

