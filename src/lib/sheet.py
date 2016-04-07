import copy

class Sheet(object):

    #
    # init
    #

    def __init__(self, valueClass=str, rowClass=list, arraydataIn=None, **kwargs):
        self.__rowClass = rowClass
        self.__valueClass = valueClass
        self.__maxColumnCount = 0
        if arraydataIn == None:
            self.setArrayData([])
        else:
            self.setArrayData(arraydataIn)
        super(Sheet, self).__init__()

    #
    # private
    #

    def __getMaxColumnCount(self):
        if self.__arraydata:
            return max(len(row) for row in self.__arraydata)
        return 0

    def __rowIsEmpty(self, row):
        """check if row is empty"""
        if len(self.__arraydata[row]) == 0:
            return True
        if max(len(cell) for cell in self.__arraydata[row]) == 0:
            return True
        return False

    def __columnIsEmpty(self, column):
        """check if column is empty"""
        for row in self.__arraydata:
            if len(row) > 0:
                if len(row) > column:
                    if len(row[column]) > 0:
                        return False
        return True

    def __removeLastRow(self):
        self.__arraydata.pop()

    def __removeLastColumn(self):
        for row in self.__arraydata:
                columnCount = len(row)
                if columnCount == self.columnCount():
                    row.pop()
        self.__maxColumnCount = self.__maxColumnCount - 1

    def __expand(self, row, column=-1):
        # rows
        if row >= 0:
            missingRows =  row - len(self.__arraydata) + 1
            if missingRows > 0:
                self.__arraydata.extend([self.__rowClass() for _ in xrange(missingRows)])
        # columns
        if column >= 0:
            missingColumns = column - len(self.__arraydata[row]) + 1
            if missingColumns > 0:
                self.__arraydata[row].extend([self.__valueClass() for _ in xrange(missingColumns)])

    def __constraint(self):
        # rows
        while self.rowCount() > 0 and self.__rowIsEmpty(-1):
            self.__removeLastRow()
        # columns
        while self.columnCount() > 0 and self.__columnIsEmpty(-1):
            self.__removeLastColumn()
        # update max column count
        self.__maxColumnCount =  self.__getMaxColumnCount()

    #
    # public
    #

    def arrayData(self):
        return self.__arraydata

    def setArrayData(self, arraydata):
        self.__arraydata = arraydata
        # constraint rows & columns
        self.__constraint()

    def rowCount(self):
        """get row count"""
        return len(self.__arraydata)

    def columnCount(self):
        """get column count"""
        return self.__maxColumnCount

    def value(self, row, column):
        """get cell value"""
        if self.rowCount() > row:
            if len(self.__arraydata[row]) > column:
                return self.__arraydata[row][column]
        return self.__valueClass('')

    def setValue(self, row, column, cellValue):
        if row < 0:
            raise IndexError('row index must be positive')
        if column < 0:
            raise IndexError('column index must be positive')
        if not isinstance(cellValue, self.__valueClass):
            raise TypeError('cellValue != ' + self.__valueClass.__class__.__name__)
        # expand rows & columns
        self.__expand(row, column)
        # set value
        self.__arraydata[row][column] = cellValue
        # constraint rows & columns
        self.__constraint()

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
        for row in self.__arraydata:
            for _ in xrange(abs(count)):
                if len(row) > index:
                    row.pop(index)
        # constraint rows & columns
        self.__constraint()

    def removeColumn(self, column):
        self.removeColumns(column, column)

    def removeRows(self, startRow, endRow):
        if startRow < 0:
            raise IndexError('row index must be positive')
        if endRow < 0:
            raise IndexError('row index must be positive')
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
            self.__arraydata.pop(index)
        # constraint rows & columns
        self.__constraint()

    def removeRow(self, row):
        self.removeRows(row, row)

    def insertRows(self, startRow, rows):
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if not rows:
            raise IndexError('rows is mandatory ')
        # expand rows
        self.__expand(startRow)
        # insert
        self.__arraydata[startRow:startRow] = rows
        # constraint rows & columns
        self.__constraint()

####    def insertEmptyRowsInColumns(self, startRow, countRow, startColumn, countColumn):
####        pass
####
####    def insertEmptyRowInColumn(self, startRow, startColumn):
####        pass

    def insertEmptyRows(self, startRow, count):
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        if startRow < self.rowCount():
            # expand rows
            self.__expand(startRow)
            # insert
            for _ in xrange(count):
                self.__arraydata.insert(startRow, [])
            # constraint rows & columns
            self.__constraint()

    def insertEmptyRow(self, row):
        self.insertEmptyRows(row, 1)

####    def insertColumns(self, startColumn, columns):
####        pass

    def insertEmptyColumnsInRows(self, startColumn, countColumn, startRow, countRow):
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if countColumn < 0:
            raise IndexError('countColumn must be greater or equal than zero')
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if countRow < 0:
            raise IndexError('countRow must be greater or equal than zero')
        if startColumn < self.columnCount():
            # expand rows & columns
            self.__expand(0, startColumn-1)
            # get end row
            endRow = startRow + countRow
            if endRow > self.rowCount():
                endRow = self.rowCount()
            # insert
            for row in self.__arraydata[startRow:endRow]:
                if len(row) >= startColumn:
                    for _ in xrange(countColumn):
                        row.insert(startColumn, self.__valueClass(''))
            # constraint rows & columns
            self.__constraint()

    def insertEmptyColumnInRow(self, startColumn, startRow):
        self.insertEmptyColumnsInRows(startColumn, 1, startRow, 1)

    def insertEmptyColumns(self, startColumn, count):
        self.insertEmptyColumnsInRows(startColumn, count, 0, self.rowCount())

    def insertEmptyColumn(self, startColumn):
        self.insertEmptyColumns(startColumn, 1)

    def moveRows(self, originRow, count, destinationRow):
        # checks
        if originRow < 0:
            raise IndexError('origin index must be positive')
        if destinationRow < 0:
            raise IndexError('destination index must be positive')
        if count < 1:
            raise IndexError('count must be higher than zero')
        if destinationRow in range(originRow, originRow+count):
            raise IndexError('destination cannot be within place to move')
        # calculate source rows empty and missing
        if originRow >= self.rowCount():
            dataRows = 0
            missingRows = count
        else:
            dataRows = min(self.rowCount() - originRow, count)
            missingRows = count - dataRows
        # move
        self.insertRows(destinationRow,
                        self.__arraydata[originRow: originRow + dataRows] + [self.__rowClass() for _ in xrange(missingRows)])
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
        for row in self.__arraydata:
            column = Sheet(valueClass=self.__valueClass,
                           rowClass=self.__valueClass,
                           arraydataIn=row)
            column.moveRows(originColumn,
                            count,
                            destinationColumn)
        # update max column count
        self.__maxColumnCount =  self.__getMaxColumnCount()

    def moveColumn(self, originColumn, destinationColumn):
        self.moveColumns(originColumn, 1, destinationColumn)


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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
            #
            self.assertEqual(sh.rowCount(), 0)
            self.assertEqual(sh.columnCount(), 0)
            self.assertEqual(sh.value(300,300), '')

        def test_setArrayData(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['', QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeRows(-2, -1)
            #
            # test 3
            #
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            with self.assertRaises(IndexError):
                sh.removeColumns(-2, -1)
            #
            # test 3: empty all
            #
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy([['1','2']]))
            sh.insertEmptyColumn(1)
            self.assertEqual(sh.arrayData(), [['1','','2']])

        def test_insert_empty_columns(self):
            arrayData = [[],
                         [QString('1-0'), QString('1-1')],
                         ['',             QString('2-1'), QString('2-2')],
                         [QString('3-0'), QString('3-1')]]
            #
            # test 1
            #
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumns(2, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 2: insert three columns to column tenth position it has no effect
            #
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumns(10, 3)
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 3)
            #
            # test 3: insert three columns to the top
            #
            sh = Sheet(valueClass=QString, arraydataIn=copy.deepcopy(arrayData))
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

        def test_insert_rows(self):
            arrayData = [['1','2'],
                         ['a','e'],
                         ['6','7'],
                         ['11','12']]
            #
            # test 1
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertRows(0, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2',], ['1','2',], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 2
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:1])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2']])
            #
            # test 3
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertRows(0, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'],['a','e'],['1','2'], ['a','e'], ['6','7'], ['11','12']])
            #
            # test 4
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertRows(4, arrayData[0:2])
            self.assertEqual(sh.arrayData(), [['1','2'], ['a','e'], ['6','7'], ['11','12'], ['1','2'], ['a','e']])
            #
            # test 5
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRow(0, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'], ['1','2','3','4','5'], ['6','7','8','9','10'], ['11','12','13','14','15']])
            #
            # test 2
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 2)
            self.assertEqual(sh.arrayData(), [['a','e','i','o','u'], ['1','2','3','4','5'], ['6','7','8','9','10'], ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 2
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(0, 2, 3)
            self.assertEqual(sh.arrayData(), [['6','7','8','9','10'],['1','2','3','4','5'],['a','e','i','o','u'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 3
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(0, 2, 2)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 4
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(3, 1, 0)
            self.assertEqual(sh.arrayData(), [['11','12','13','14','15'],['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 5
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(3, 1, 6)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],['a','e','i','o','u'],['6','7','8','9','10'],[],[],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 6
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],[], [],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 7
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(3, 2, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'], ['11','12','13','14','15'], [], ['a', 'e', 'i', 'o', 'u'], ['6', '7', '8', '9', '10']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 8
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(5, 1, 1)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],[],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 9
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 0)
            self.assertEqual(sh.arrayData(), [[], [],['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 6)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 10
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(5, 2, 4)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 11
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(50, 20, 40)
            self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 12
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 5)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15'],[],['1', '2', '3', '4', '5']])
            self.assertEqual(sh.rowCount(), 5)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 13
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveRows(0, 1, 7)
            self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],['6', '7', '8', '9', '10'],['11','12','13','14','15'],[],[],[],['1', '2', '3', '4', '5']])
            self.assertEqual(sh.rowCount(), 7)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 14
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
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
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveColumns(0, 1, 6)
            self.assertEqual(sh.arrayData(), [['2','3','4','5','','1'],
                                              ['e','i','o','u','','a'],
                                              ['7','8','9','10','','6'],
                                              ['12','13','14','15','','11']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 4
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.moveColumns(50, 2, 100)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)

        def test_move_insert_empty_columns_inrows(self):
            arrayData = [['1','2','3','4','5'],
                         ['a','e','i','o','u'],
                         ['6','7','8','9','10'],
                         ['11','12','13','14','15']]
            #
            # test 1: insert a new cell in row zero
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=2,
                                        countColumn=1,
                                        startRow=0,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 2: insert two new cells in row zero
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=2,
                                        countColumn=2,
                                        startRow=0,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','','','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 7)
            #
            # test 3: insert one empty cell to column fifth position it has no effect
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=5,
                                        countColumn=1,
                                        startRow=0,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 4: insert two empty cell to row fourth it has no effect
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=4,
                                        countColumn=2,
                                        startRow=4,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 5: insert a new cell in last row
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=2,
                                        countColumn=1,
                                        startRow=3,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 6: insert two new cells in last row
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnsInRows(startColumn=2,
                                        countColumn=2,
                                        startRow=3,
                                        countRow=1)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','','','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 7)

        def test_move_insert_empty_column_inrow(self):
            arrayData = [['1','2','3','4','5'],
                         ['a','e','i','o','u'],
                         ['6','7','8','9','10'],
                         ['11','12','13','14','15']]
            #
            # test 1: insert a new cell in row zero
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnInRow(startColumn=2,
                                      startRow=0)
            self.assertEqual(sh.arrayData(), [['1','2','','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)
            #
            # test 3: insert one empty cell to column fifth position it has no effect
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnInRow(startColumn=5,
                                      startRow=0)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 5)
            #
            # test 5: insert a new cell in last row
            #
            sh = Sheet(arraydataIn=copy.deepcopy(arrayData))
            sh.insertEmptyColumnInRow(startColumn=2,
                                      startRow=3)
            self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                              ['a','e','i','o','u'],
                                              ['6','7','8','9','10'],
                                              ['11','12','','13','14','15']])
            self.assertEqual(sh.rowCount(), 4)
            self.assertEqual(sh.columnCount(), 6)



    unittest.main()

