import copy

class Sheet(object):

    #
    # init
    #

    def __init__(self, valueClass=str, arraydataIn=[]):
        self._valueClass = valueClass
        self._maxColumnCount = 0
        self.setArrayData(copy.deepcopy(arraydataIn))
        super(Sheet, self).__init__()

    #
    # private
    #

    def _getMaxColumnCount(self):
        if self._arraydata:
            return max(len(row) for row in self._arraydata)
        return 0

    def _rowIsEmpty(self, row):
        """check if row is empty"""
        if len(self._arraydata[row]) == 0:
            return True
        if max(len(cell) for cell in self._arraydata[row]) == 0:
            return True
        return False

    def _columnIsEmpty(self, column):
        """check if column is empty"""
        for row in self._arraydata:
            if len(row) > 0:
                if len(row) > column:
                    if len(row[column]) > 0:
                        return False
        return True

    def _removeLastRow(self):
        self._arraydata.pop()

    def _removeLastColumn(self):
        for row in self._arraydata:
                columnCount = len(row)
                if columnCount == self.columnCount():
                    row.pop()
        self._maxColumnCount = self._maxColumnCount - 1

    def _expand(self, row, column):
        # rows
        missingRows =  row - len(self._arraydata) + 1
        self._arraydata.extend([[] for _ in xrange(missingRows)])
        # columns
        missingColumns = column - len(self._arraydata[row]) + 1
        self._arraydata[row].extend([self._valueClass('')]*missingColumns)

    def _constraint(self):
        # rows
        while self.rowCount() > 0 and self._rowIsEmpty(-1):
            self._removeLastRow()
        # columns
        while self.columnCount() > 0 and self._columnIsEmpty(-1):
            self._removeLastColumn()
        # update max column count
        self._maxColumnCount =  self._getMaxColumnCount()

    #
    # public
    #

    def arrayData(self):
        return self._arraydata

    def setArrayData(self, arraydata):
        self._arraydata = arraydata
        # constraint rows & columns
        self._constraint()

    def rowCount(self):
        """get row count"""
        return len(self._arraydata)

    def columnCount(self):
        """get column count"""
        return self._maxColumnCount

    def value(self, row, column):
        """get cell value"""
        if self.rowCount() > row:
            if len(self._arraydata[row]) > column:
                return self._arraydata[row][column]
        return self._valueClass('')

    def setValue(self, row, column, cellValue):
        if row < 0:
            raise IndexError('row index must be positive')
        if column < 0:
            raise IndexError('column index must be positive')
        if not isinstance(cellValue, self._valueClass):
            raise TypeError('cellValue != ' + self._valueClass.__class__.__name__)
        # expand rows & columns
        self._expand(row, column)
        # set value
        self._arraydata[row][column] = cellValue
        # constraint rows & columns
        self._constraint()

    def removeColumns(self, startColumn, endColumn):
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
        count = endColumn - startColumn + 1
        index = startColumn
        if startColumn < 0:
            index = endColumn
        for row in self._arraydata:
            for _ in xrange(abs(count)):
                if len(row) > index:
                    row.pop(index)
        # constraint rows & columns
        self._constraint()

    def removeColumn(self, column):
        self.removeColumns(column, column)

    def removeRows(self, startRow, endRow):
        if startRow < 0:
            raise IndexError('row index must be positive')
        if endRow < 0:
            raise IndexError('row inde must be positive')
        if startRow >= self.rowCount():
            raise IndexError('row index out of range')
        if endRow >= self.rowCount():
            raise IndexError('row index out of range')
        if endRow < startRow:
            raise IndexError('startRow must be smaller than endRow')
        count = endRow - startRow + 1
        index = startRow
        if startRow < 0:
            index = endRow
        for _ in xrange(abs(count)):
            self._arraydata.pop(index)
        # constraint rows & columns
        self._constraint()

    def removeRow(self, row):
        self.removeRows(row, row)

    def insertRows(self, startRow, rows):
        if startRow < 0:
            raise IndexError('startRow index must be positive')
        if not rows:
            raise IndexError('rows is mandatory ')
        # expand rows & columns
        self._expand(startRow, 0)
        # insert
        self._arraydata[startRow:startRow] = rows
        # constraint rows & columns
        self._constraint()

    def insertEmptyRows(self, startRow, count):
        if startRow < 0:
            raise IndexError('row index must be positive')
        if count < 1:
            raise IndexError('count must higher than zero')
        if startRow < self.rowCount():
            # expand rows & columns
            self._expand(startRow, 0)
            # insert
            for _ in xrange(count):
                self._arraydata.insert(startRow,[])
            # constraint rows & columns
            self._constraint()

    def insertEmptyRow(self, row):
        self.insertEmptyRows(row, 1)

    #def insertColumns(self, startColumn, columns):
    #    pass

    def insertEmptyColumns(self, startColumn, count):
        if startColumn < 0:
            raise IndexError('column index must be positive')
        if count < 1:
            raise IndexError('count must higher than zero')
        if startColumn < self.columnCount():
            # expand rows & columns
            self._expand(0, startColumn-1)
            # insert
            for row in self._arraydata:
                if len(row) >= startColumn:
                    for _ in xrange(count):
                        row.insert(startColumn, self._valueClass(''))
            # constraint rows & columns
            self._constraint()

    def insertEmptyColumn(self, startColumn):
        self.insertEmptyColumns(startColumn, 1)

    def moveRows(self, originRow, count, destinationRow):
        # checks
        if originRow < 0:
            raise IndexError('originRow index must be positive')
        if destinationRow < 0:
            raise IndexError('destinationRow index must be positive')
        if count < 1:
            raise IndexError('count must be higher than zero')
        if destinationRow in range(originRow, originRow+count):
            raise IndexError('destinationRow cannot be within rows to move')
        # calculate source rows empty and missing
        if originRow >= self.rowCount():
            dataRows = 0
            missingRows = count
        else:
            dataRows = min(self.rowCount() - originRow, count)
            missingRows = count - dataRows
        # move
        self.insertRows(destinationRow,
                        self._arraydata[originRow: originRow + dataRows] + [[] for _ in xrange(missingRows)])
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
        pass
##        # checks
##        if originColumn < 0:
##            raise IndexError('originColumn index must be positive')
##        if destinationColumn < 0:
##            raise IndexError('destinationColumn index must be positive')
##        if count < 1:
##            raise IndexError('count must be higher than zero')
##        if destinationColumn in range(originColumn, originColumn+count):
##            raise IndexError('destinationColumn cannot be within columns to move')
##        #
##        self.insertEmptyColumns(destinationColumn, count)
##        # loop rows
##        for index, row in enumerate(self._arraydata):
##            # calculate source columns empty and missing
##            columnCount = len(row)
##            if originColumn >= columnCount:
##                dataColumns = 0
##                missingColumns = count
##            else:
##                dataColumns = min(columnCount - originColumn, count)
##                missingColumns = count - dataColumns
##            # move       
##            self.setValue( 
##            row[originColumn: originColumn + dataColumns] + [self._valueClass('')] * for _ in xrange(missingColumns)])
##            if dataColumns > 0:
##                if destinationColumn < originColumn:
##                    self.removeColumns(originColumn + count,
##                                       originColumn + count + dataColumns - 1)
##                else:
##                    self.removeColumns(originColumn,
##                                       originColumn + dataColumns - 1)

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
            sh2 = Sheet(valueClass=QString)
            self.assertEqual(sh2.rowCount(), 0)
            self.assertEqual(sh2.columnCount(), 0)

        def test_setvalue_default_class(self):
            sh = Sheet()
            #
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
            #
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

        def test_emptySetArrayData(self):
            arrayData = []
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
            #
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            self.assertEqual(sh.value(300,300), '')

        def test_setArrayData(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['', QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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

        def test_remove_rows(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['', QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeRows(-2, -1)
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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

        def test_remove_columns(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeColumns(-2, -1)
            #
            # test 3: empty all
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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


        def test_insert_empty_row(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            #
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            # test 5: count higher than zero
            #
            sh = Sheet(valueClass=QString)
            with self.assertRaises(IndexError):
                sh.insertEmptyRows(2, 0)

        def test_insert_empty_column(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1: insert one column to the middle
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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

        def test_insert_empty_columns(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
            sh.insertEmptyColumns(2, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 2: insert three columns to column tenth position it has no effect
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
            sh.insertEmptyColumns(10, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            # test 3: insert three columns to the top
            #
            sh = Sheet(valueClass=QString, arraydataIn=arrayData)
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
            # test 5: count higher than zero
            #
            sh = Sheet(valueClass=QString)
            with self.assertRaises(IndexError):
                sh.insertEmptyColumns(2, 0)

        def test_insert_rows(self):
            arrayData = [['1','2'], ['a','e'], ['6','7'], ['11','12']]
            #
            # test 1
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.insertRows(0, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2',], ['1','2',], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 2
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.insertRows(4, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2']])
            #
            # test 3
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.insertRows(0, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],['a','e'],['1','2'], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 4
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.insertRows(4, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2'], ['a','e']])
            #
            # test 5
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.insertRows(6, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'],[],[],['1','2'], ['a','e']])

        def test_move_row(self):
            arrayData = [['1','2','3','4','5'],
                        ['a','e','i','o','u'],
                        ['6','7','8','9','10'],
                        ['11','12','13','14','15']]
            #
            # test 1
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRow(0, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'], ['1','2','3','4','5'], ['6','7','8','9','10'], ['11','12','13','14','15']])
            #
            # test 2
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRow(2, 5)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],['a','e','i','o','u'],['11','12','13','14','15'],[],['6','7','8','9','10']])


        def test_move_rows(self):
            arrayData = [['1','2','3','4','5'],
                        ['a','e','i','o','u'],
                        ['6','7','8','9','10'],
                        ['11','12','13','14','15']]
            #
            # test 1
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(0, 1, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'], ['1','2','3','4','5'], ['6','7','8','9','10'], ['11','12','13','14','15']])
            #
            # test 2
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(0, 2, 3)
            self.assertEqual(sh.arrayData(), [['6','7','8','9','10'],['1','2','3','4','5'],['a','e','i','o','u'],['11','12','13','14','15']])
            #
            # test 3
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(0, 2, 2)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10'],['11','12','13','14','15']])
            #
            # test 4
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(3, 1, 0)
            self.assertEqual(sh.arrayData(), [['11','12','13','14','15'],['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10']])
            #
            # test 5
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(3, 1, 6)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10'],[],[],['11','12','13','14','15']])
            #
            # test 6
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(5, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],[], [],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            #
            # test 7
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(3, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'], ['11','12','13','14','15'], [], ['a', 'e', 'i', 'o', 'u'], ['6', '7', '8', '9', '10']])
            #
            # test 8
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(5, 1, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],[],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            #
            # test 9
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(5, 2, 0)
            self.assertEqual(sh.arrayData(), [[], [],['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            #
            # test 10
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(5, 2, 4)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            #
            # test 11
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(50, 20, 40)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            #
            # test 12
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(0, 1, 5)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15'],[],['1', '2', '3', '4', '5']])
            #
            # test 13
            #
            sh = Sheet(arraydataIn=arrayData)
            sh.moveRows(0, 1, 7)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15'],[],[],[],['1', '2', '3', '4', '5']])
            #
            # test 14
            #
            sh = Sheet(arraydataIn=arrayData)
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

    unittest.main()



