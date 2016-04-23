from PyQt4.QtCore import *
import copy
import numpy as np
import lib.enums as enums
import lib.helper as helper
import re


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

    def removeColumns(self, startColumn, count):
        # check
        if startColumn < 0:
            raise IndexError('column index must be positive')
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        if startColumn >= self.columnCount():
            return
        # remove
        endColumn = startColumn + count
        if endColumn > self.columnCount():
            endColumn = self.columnCount()
        self.__arrayData = np.delete(self.__arrayData, xrange(startColumn, endColumn), axis=1)
        # constraint rows & columns
        self.__constraint()

    def removeColumn(self, column):
        self.removeColumns(column, 1)

    def removeRows(self, startRow, count):
        # check
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        if startRow >= self.rowCount():
            return
        # remove
        endRow = startRow + count
        if endRow >  self.rowCount():
            endRow = self.rowCount()
        self.__arrayData = np.delete(self.__arrayData, xrange(startRow, endRow), axis=0)
        # constraint rows & columns
        self.__constraint()

    def removeRow(self, row):
        self.removeRows(row, 1)

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
            # expand columns array
            missingRows = max(self.rowCount() - len(columns), 0)
            if missingRows > 0:
                emptyRows = np.empty([missingRows, len(columns[0])], dtype=object)
                columns = np.concatenate((columns, emptyRows), axis=0)
            # insert columns
            self.insertArrayInColumns(startRow=0,
                                      startColumn=startColumn,
                                      array=columns)

    def insertEmptyColumns(self, startColumn, count):
        # check
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if count < 0:
            raise IndexError('count must be greater or equal than zero')
        # insert
        if self.rowCount() > 0:
            self.insertEmptyCellsInColumns(startRow=0,
                                           startColumn=startColumn,
                                           dimRows=self.rowCount(),
                                           dimColumns=count)

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
                                count + dataRows)
            else:
                self.removeRows(originRow,
                                dataRows)

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
                           self.__arrayData[:, originColumn: originColumn + dataColumns].tolist())
        if missingColumns > 0:
            self.insertEmptyColumns(destinationColumn + dataColumns, missingColumns)
        if dataColumns > 0:
            if destinationColumn < originColumn:
                self.removeColumns(originColumn + count,
                                   count + dataColumns)
            else:
                self.removeColumns(originColumn,
                                   dataColumns)

    def moveColumn(self, originColumn, destinationColumn):
        self.moveColumns(originColumn, 1, destinationColumn)

    def insertArrayInColumns(self, startRow, startColumn, array):
        """
        Insert array and move the affected columns downward

        :param int startRow: Row number where to insert array
        :param int startColumn: Column number where to insert array
        :param [[]] array: Array to insert
        :return: True, if modified anything
        :rtype: bool
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
                # add empty columns at right
                missingColumns = max(startColumn - destColumns, 0) + sourceColumns
                emptyColumns = np.empty([destRows, missingColumns], dtype=object)
                self.__arrayData = np.concatenate((self.__arrayData, emptyColumns), axis=1)
                # add empty rows at last
                missingRows = startRow + sourceRows - self.rowCount()
                if missingRows > 0:
                    emptyRows = np.empty([missingRows, self.columnCount()], dtype=object)
                    self.__arrayData = np.concatenate((self.__arrayData, emptyRows), axis=0)
                # copy slice array to new position
                self.__arrayData[startRow:startRow+sourceRows, startColumn+sourceColumns:destColumns+sourceColumns] = \
                                 self.__arrayData[startRow:startRow+sourceRows, startColumn:destColumns]

             #   self.__arrayData[startRow+sourceRows:destRows+sourceRows, startColumn:startColumn+sourceColumns] = \
             #                    self.__arrayData[startRow:destRows, startColumn:startColumn+sourceColumns]
            else:
                self.__arrayData = np.empty([startRow+sourceRows, startColumn+sourceColumns], dtype=object)
            # set values
            self.__arrayData[startRow:startRow+sourceRows, startColumn:startColumn+sourceColumns] = sourceArray
            # constraint rows & columns
            self.__constraint()
            return True

    def insertEmptyCellsInColumns(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        sourceArray = np.empty([dimRows, dimColumns], dtype=object)
        return self.insertArrayInColumns(startRow, startColumn, sourceArray)

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
                    emptyColumns = np.empty([self.rowCount(), missingColumns], dtype=object)
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
            return True

    def insertEmptyCellsInRows(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        sourceArray = np.empty([dimRows, dimColumns], dtype=object)
        return self.insertArrayInRows(startRow, startColumn, sourceArray)

    def removeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if not self.isEmpty():
            endRow = min(startRow + dimRows, self.rowCount())
            endColumn =  self.columnCount() - dimColumns
            #
            originStartRow = startRow
            originEndRow = endRow
            originStartColumn = startColumn + dimColumns
            originEndColumn = self.columnCount()
            #
            emptyStartRow = startRow
            emptyEndRow = endRow
            emptyStartColumn = max(startColumn, endColumn)
            emptyEndColumn = self.columnCount()
            #
            if startColumn <= endColumn:
                self.__arrayData[startRow:endRow, startColumn:endColumn] = self.__arrayData[originStartRow:originEndRow, originStartColumn:originEndColumn]
            if emptyStartColumn <= emptyEndColumn:
                self.__arrayData[emptyStartRow:emptyEndRow, emptyStartColumn:emptyEndColumn] = None
            # constraint rows & columns
            self.__constraint()
            return True

    def removeArrayInRows(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if not self.isEmpty():
            endRow =  self.rowCount() - dimRows
            endColumn =  min(startColumn + dimColumns, self.columnCount())
            #
            originStartRow = startRow + dimRows
            originEndRow = self.rowCount()
            originStartColumn = startColumn
            originEndColumn = endColumn
            #
            emptyStartRow = max(startRow, endRow)
            emptyEndRow = self.rowCount()
            emptyStartColumn =  startColumn
            emptyEndColumn = endColumn
            #
            if startRow <= endRow:
                self.__arrayData[startRow:endRow, startColumn:endColumn] = self.__arrayData[originStartRow:originEndRow, originStartColumn:originEndColumn]
            if emptyStartRow <= emptyEndRow:
                self.__arrayData[emptyStartRow:emptyEndRow, emptyStartColumn:emptyEndColumn] = None
            # constraint rows & columns
            self.__constraint()
            return True

    def deleteCells(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if startRow < self.rowCount() and startColumn < self.columnCount():
            # get end row & column
            endRow = startRow + dimRows
            endColumn = startColumn + dimColumns
            if endRow > self.rowCount():
                endRow = self.rowCount()
            if endColumn > self.columnCount():
                endColumn = self.columnCount()
            # set values
            self.__arrayData[startRow:endRow, startColumn:endColumn] = None
            # constraint rows & columns
            self.__constraint()

    def search(self, text, matchMode, matchCaseOption):
        """search data in CSV
           return [row,col,value],..]
        """
        result = []
        # need convert to unicode format
        text = helper.QStringToUnicode(text)
        # set regular expression pattern
        if matchMode == enums.MatchModeEnum.WholeWord:
            pattern = ur'\b{0}\b'.format(text)                   #  ur = unicode + raw string
        elif matchMode == enums.MatchModeEnum.StartsWidth:
            pattern = ur'^{0}'.format(text)
        elif matchMode == enums.MatchModeEnum.EndsWith:
            pattern = ur'{0}$'.format(text)
        elif matchMode == enums.MatchModeEnum.RegularExpression:
            pattern = ur'{0}'.format(text)
        else:
            pattern = ur''
        # compile regular expression
        if matchCaseOption:
            rePattern = re.compile(pattern, flags=re.DOTALL|re.UNICODE)
        else:
            rePattern = re.compile(pattern, flags=re.IGNORECASE|re.DOTALL|re.UNICODE)
        # search
        for numRow, dataRow in enumerate(self.__arrayData):
            for numCol, dataCell in enumerate(dataRow):
                if dataCell != None:
                    find = False
                    if matchMode == enums.MatchModeEnum.Contains:
                        if matchCaseOption:
                            find = dataCell.contains(text, Qt.CaseSensitive)
                        else:
                            find = dataCell.contains(text, Qt.CaseInsensitive)
                    else:
                        find = rePattern.search(dataCell)
                    if find:
                        result.append([numRow, numCol, dataCell])
        return result

    def getArray(self, startRow, startColumn, dimRows, dimColumns):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        # get array
        endRow = startRow+dimRows
        endColumn = startColumn+dimColumns
        self.__expand(endRow, endColumn)
        array = self.__arrayData[startRow:endRow, startColumn:endColumn]
        self.__constraint()
        return copy.deepcopy(array)

    def moveArrayInRows(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if destRow < 0:
            raise IndexError('destRow must be positive')
        if destColumn < 0:
            raise IndexError('destColumn must be positive')
        array = self.getArray(startRow, startColumn, dimRows, dimColumns)
        self.removeArrayInRows(startRow, startColumn, dimRows, dimColumns)
        self.insertArrayInRows(destRow, destColumn, array)
        return True
