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
        if arrayData != None:
            self.setArrayData(arrayData)
        else:
            self.setArrayData([])
        super(Sheet, self).__init__()

    #
    # private
    #

    def __expandColumnsArray(self, arrayData, column):
        """expand up column specified in a python array """
        if arrayData != None:
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

    def __getNumpyArray(self, sourceArray):
        if sourceArray != None:
            dimRows = len(sourceArray)
            if dimRows:
                dimColumns = max(len(row) for row in sourceArray)
            else:
                dimColumns = 0
            numpyArray = np.empty((dimRows, dimColumns), dtype=object)  # numpy array error with QString arrays
            numpyArray[:] = sourceArray                                 # http://stackoverflow.com/q/36931732/2270217
            return numpyArray
        else:
            return None

    #
    # public
    #

    def arrayData(self):
        """get array"""
        # numpy array -> array
        return self.__arrayData.tolist()

    def setArrayData(self, arrayData):
        """set array"""
        # all rows must have the same columns number
        if arrayData:
            maxColumnSize = max(len(row) for row in arrayData)
            for row in arrayData:
                missingColumns = maxColumnSize - len(row)
                if missingColumns > 0:
                    row.extend([None for _ in xrange(missingColumns)])
        # array to numpy array
        self.__arrayData = self.__getNumpyArray(arrayData)

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
        if rows != None:
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
        if columns != None:
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
        sourceArray = self.__getNumpyArray(array)
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

    def getArray(self, startRow, startColumn, dimRows, dimColumns, transpose=False):
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
        if transpose:
            return np.transpose(copy.deepcopy(array))
        else:
            return copy.deepcopy(array)

    def setArray(self, startRow, startColumn, array):
        """paste array at the given coordinates
        """
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        # set array
        sourceArray = self.__getNumpyArray(array)
        if sourceArray.size > 0:
            dimRows = sourceArray.shape[0]
            dimColumns = sourceArray.shape[1]
            self.removeArrayInRows(startRow, startColumn, dimRows, dimColumns)
            self.insertArrayInRows(startRow, startColumn, array)

    def setArrayRepeater(self, startRow, startColumn, dimRows, dimColumns, array):
        """paste array in the coordinates indicated repeating the glue-down selection
        """
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        # set array repeater
        sourceArray = self.__getNumpyArray(array)
        if sourceArray.size > 0:
            dimArrayRows = sourceArray.shape[0]
            dimArrayColumns = sourceArray.shape[1]
            repeatInSelection = ((dimRows % dimArrayRows) + (dimColumns % dimArrayColumns) == 0)
            if repeatInSelection:
                for numRow in xrange(dimRows / dimArrayRows):
                    for numColumn in xrange(dimColumns / dimArrayColumns):
                        self.setArray(startRow + (dimArrayRows * numRow),
                                      startColumn + (dimArrayColumns * numColumn),
                                      array)
            else:
                self.setArray(startRow, startColumn, array)

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

    def moveArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn):
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
        self.removeArrayInColumns(startRow, startColumn, dimRows, dimColumns)
        self.insertArrayInColumns(destRow, destColumn, array)
        return True

    def moveRows(self, startRow, count, destinationRow):
         self.moveArrayInRows(startRow,
                              0,
                              count,
                              self.columnCount(),
                              destinationRow,
                              0)

    def moveRow(self, originRow, destinationRow):
        self.moveRows(originRow, 1, destinationRow)

    def moveColumns(self, startColumn, count, destinationColumn):
        self.moveArrayInColumns(0,
                                startColumn,
                                self.rowCount(),
                                count,
                                0,
                                destinationColumn)

    def moveColumn(self, originColumn, destinationColumn):
        self.moveColumns(originColumn, 1, destinationColumn)

    def mergeArrayInRows(self, startRow, startColumn, dimRows, dimColumns, separator=None):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if separator == None:
            separator = ' '
        # get array
        array = self.getArray(startRow, startColumn, dimRows, dimColumns)
        # merge array
        mergedArray = []
        for xcolumn in xrange(array.shape[1]):
            acolumns = array[:, xcolumn]
            if self.__valueClass == QString:
                acolumns = [helper.QStringToUnicode(value) for value in acolumns if value]
                value = separator.join(acolumns)
                mergedArray.append(self.__valueClass(value))
            else:
                acolumns = [value for value in acolumns if value]
                value = separator.join(acolumns)
                mergedArray.append(value)
        # convert array to numpy array
        merged = np.empty((1, dimColumns), dtype=object)      # numpy array error with QString arrays
        merged[:] = [mergedArray]                             # http://stackoverflow.com/q/36931732/2270217
        # remove array to merged
        self.removeArrayInRows(startRow, startColumn, dimRows, dimColumns)
        # insert merged array
        self.insertArrayInRows(startRow, startColumn, merged)
        return True

    def mergeRows(self, startRow, rows, separator=None):
        self.mergeArrayInRows(startRow,
                              0,
                              rows,
                              self.columnCount(),
                              separator)

    def mergeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, separator=None):
        # checks
        if startRow < 0:
            raise IndexError('startRow must be positive')
        if startColumn < 0:
            raise IndexError('startColumn must be positive')
        if dimRows < 1:
            raise IndexError('dimRows must be higher than zero')
        if dimColumns < 1:
            raise IndexError('dimColumns must be higher than zero')
        if separator == None:
            separator = ' '
        # get array
        array = self.getArray(startRow, startColumn, dimRows, dimColumns)
        # merge array
        mergedArray = []
        for xrow in xrange(array.shape[0]):
            arows = array[xrow, :]
            if self.__valueClass == QString:
                arows = [helper.QStringToUnicode(value) for value in arows if value]
                value = separator.join(arows)
                mergedArray.append([self.__valueClass(value)])
            else:
                arows = [value for value in arows if value]
                value = separator.join(arows)
                mergedArray.append([value])
        # convert array to numpy array
        merged = np.empty((dimRows, 1), dtype=object)      # numpy array error with QString arrays
        merged[:] = mergedArray                            # http://stackoverflow.com/q/36931732/2270217
        # remove array to merged
        self.removeArrayInColumns(startRow, startColumn, dimRows, dimColumns)
        # insert merged array
        self.insertArrayInColumns(startRow, startColumn, merged)
        return True

    def mergeColumns(self, startColumn, columns, separator=None):
        self.mergeArrayInColumns(0,
                                 startColumn,
                                 self.rowCount(),
                                 columns,
                                 separator)

