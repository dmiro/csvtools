# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.config import config
from lib.helper import get_size
from lib.enums import MatchModeEnum
from datetime import datetime
import os
import re

##class NumberSortModel(QSortFilterProxyModel):
##    def lessThan(self, left, right):
##        lvalue = left.data().toDouble()[0]
##        rvalue = right.data().toDouble()[0]
##        return lvalue < rvalue


class StringSortModel(QSortFilterProxyModel):
    def lessThan(self, left, right):
        lvalue = left.data().toString().toUpper()
        rvalue = right.data().toString().toUpper()
        return lvalue < rvalue


class MyTableView(QTableView):
    def __init__(self, average, items, sum_, parent = None, *args):
        QTableView.__init__(self, parent, *args)
        self.average = average
        self.items = items
        self.sum_ = sum_
        self.setSortingEnabled(True)

class QItemDataBorderDelegate(QStyledItemDelegate):
    def __init__ (self, parent = None):
        super(QItemDataBorderDelegate, self).__init__ (parent)

    def paint(self, painter, option, index):
        if index:
            model = index.model()
            if model:
                rowIndex = index.row()
                columnIndex = index.column()
                columnDataCount = model.columnDataCount()-1
                rowDataCount = model.rowDataCount()-1
                if (rowDataCount == rowIndex) and (columnIndex <= columnDataCount):
                    painter.setPen(QPen(Qt.red, 1, style=Qt.DotLine))
                    painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
                if (columnDataCount == columnIndex) and (rowIndex <= rowDataCount):
                    painter.setPen(QPen(Qt.red, 1, style=Qt.DotLine))
                    painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
        super(QItemDataBorderDelegate, self).paint(painter, option, index)


class MyTableModel(QAbstractTableModel):

    #
    # private
    #

    def _getMaxDataColumn(self):
        return max(len(row) for row in self.arraydata)

    def _rowIsEmpty(self, rowIndex):
        if len(self.arraydata[rowIndex]) == 0:
            return True
        if max(len(cell) for cell in self.arraydata[rowIndex]) == 0:
            return True
        return False

    def _columnIsEmpty(self, columnIndex):
        for row in self.arraydata:
            if len(row) > columnIndex:
                if len(row[columnIndex]) > 0:
                    return False
        return True

    def _deleteColumn(self, columnIndex):
        for row in self.arraydata:
            if len(row) > columnIndex:
                del(row[columnIndex])

    #
    # public
    #

    def setRowCorner(self, value):
        """specify the row of the cell visible at top-left corner.
        The value is set by QTableView"""
        rowCount = self.rowCount()
        self.beginInsertRows(QModelIndex(), rowCount, rowCount+1)
        self.rowCorner = value
        self.endInsertRows()

    def setColumnCorner(self, value):
        """specify the column of the cell visible at top-left corner.
        The value is set by QTableView"""
        columnCount = self.columnCount()
        self.beginInsertColumns(QModelIndex(), columnCount, columnCount+1)
        self.columnCorner = value
        self.endInsertColumns()

    def rowDataCount(self, parent=QModelIndex()):
        """get row count real data"""
        if self.headerrow:
            return len(self.arraydata)-1
        else:
            return len(self.arraydata)

    def columnDataCount(self, parent=QModelIndex()):
        """get column count real data"""
        return self._maxDataColumn

    def rowCount(self, parent=QModelIndex()):
        """get the total virtual rows calculated based on the number of actual
        rows and the visible row in the top-left corner"""
        row = self.rowCorner + 100
        if row < self.rowDataCount():
            return self.rowDataCount()
        return row

    def columnCount(self, parent=QModelIndex()):
        """get the total virtual columns calculated based on the number of actual
        rows and the visible column in the top-left corner"""
        column = self.columnCorner + 100
        if column < self.columnDataCount():
            return self.columnDataCount()
        return column

    def setPointSize(self, pointSize):
        self.pointSize = pointSize

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self.headerrow and role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return QVariant(self.arraydata[0][section])
        elif role == Qt.FontRole:
            font = QFont()
            font.setPointSize(self.pointSize)
            return font
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.FontRole:
            #return QFont('Courier New', 6, QFont.Bold);
            #return QFont('Courier New', self.size, QFont.Bold);
            font = QFont()
            font.setPointSize(self.pointSize)
            return font
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            rowIndex = index.row()
            columnIndex = index.column()
            if self.headerrow:
                rowIndex = rowIndex + 1
            if len(self.arraydata) > (rowIndex):
                if len(self.arraydata[rowIndex]) > columnIndex:
                    return QVariant(self.arraydata[rowIndex][columnIndex])
#        elif role == Qt.BackgroundRole:
#            return QBrush(QColor(8, 8, 8, 8))
##        elif role == Qt.BackgroundRole:
##            rowIndex = index.row()
##            columnIndex = index.column()
##            if self.rowDataCount() > rowIndex:
##                if self.columnDataCount() > columnIndex:
##                    return QBrush(QColor(8, 8, 8, 8))
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # calculate row and column index
            rowIndex = index.row()
            columnIndex = index.column()
            if self.headerrow:
                rowIndex = rowIndex + 1
            # expand rows
            if len(self.arraydata) <= rowIndex:
                rowsMissing =  rowIndex - len(self.arraydata) + 1
                self.arraydata.extend([[] for _ in xrange(rowsMissing) ])
            # expand columns
            if len(self.arraydata[rowIndex]) <= columnIndex:
                columnsMissing = columnIndex - len(self.arraydata[rowIndex]) + 1
                self.arraydata[rowIndex].extend(['']*columnsMissing)
            # set value
            self.arraydata[rowIndex][columnIndex] = value.toString()
            # if required, constraint rows
            if len(self.arraydata) - 1 == rowIndex:
                if value.toString().isEmpty():
                    while rowIndex > 0 and self._rowIsEmpty(-1):
                        self.arraydata.pop()
                        rowIndex = rowIndex - 1
            # if required, constraint columns
            if len(self.arraydata[rowIndex]) - 1 == columnIndex:
                if value.toString().isEmpty():
                    while columnIndex > 0 and self._columnIsEmpty(columnIndex):
                       self._deleteColumn(columnIndex)
                       columnIndex = columnIndex - 1
            # update max data column
            if len(self.arraydata[rowIndex]) > self._maxDataColumn:
                self._maxDataColumn = len(self.arraydata[rowIndex])
            elif len(self.arraydata[rowIndex]) < self._maxDataColumn:
                self._maxDataColumn =  self._getMaxDataColumn()
            # emit data changed
            bottomRight = self.createIndex(self.rowCount(), self.columnCount())
            self.dataChanged.emit(index, bottomRight)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRows(self, row, count, parent = QModelIndex()):
        self.beginInsertRows(parent, row, row+count)
        for _ in xrange(count):
            self.arraydata.insert(row,[])
        self._maxDataColumn = self._getMaxDataColumn()
        self.endInsertRows()
        return True

    def insertRow(self, row, parent = QModelIndex()):
        return self.insertRows(row, 1, parent)

    def insertColumns(self, column, count, parent = QModelIndex()):
        self.beginInsertColumns(parent, column, column+count)
        for row in self.arraydata:
            if len(row) > column:
                for _ in xrange(count):
                    row.insert(column, '')
        self._maxDataColumn = self._getMaxDataColumn()
        self.endInsertColumns()
        return True

    def insertColumn(self, column, parent = QModelIndex()):
        return self.insertColumn(column, 1, parent)

    #
    # init
    #

    def __init__(self, datain, headerrow=False, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.headerrow= headerrow
        self.arraydata= datain
        self.pointSize= QFont().pointSize()
        self.columnCorner = 0
        self.rowCorner = 0
        self._maxDataColumn = self._getMaxDataColumn()

class QCsv(QTableView):

    #
    # private
    #

    # http://stackoverflow.com/questions/11352523/qt-and-pyqt-tablewidget-growing-row-count
    # http://stackoverflow.com/questions/19993898/dynamically-add-data-to-qtableview
    # http://permalink.gmane.org/gmane.comp.python.pyqt-pykde/25792
    def _scrollbarChangedEvent(self, val):
        indexCorner = self.indexAt(QPoint(1,1))
        model = self.model()
        model.setColumnCorner(indexCorner.column())
        model.setRowCorner(indexCorner.row())

    def selectionChanged (self, selected, deselected):
        self.selectionChanged_.emit()
        return QTableView.selectionChanged (self, selected, deselected)

    def _customContextMenuRequestedEvent(self, point):
        if len(self.selectedIndexes()) > 0:
            self.contextMenuRequested.emit(self.selectedIndexes(), self.mapToGlobal(point))

    def _getHeaderRows(self):
        result = []
        model = self.model()
        columnCount = model.columnCount(None)
        for column in xrange(columnCount):
            data = model.headerData(column, orientation = Qt.Horizontal)
            result.append(data.toString())
        return result

    def _select(self, topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn):
        # create item selection
        model = self.model()
        topLeft = model.createIndex(topLeftRow, topLeftColumn)
        bottomRight = model.createIndex(bottomRightRow, bottomRightColumn)
        selection = QItemSelection(topLeft, bottomRight)
        # select items
        selectionModel = self.selectionModel()
        selectionModel.select(selection, QItemSelectionModel.Select)

    #
    # public
    #

    selectionChanged_ = pyqtSignal()
    contextMenuRequested = pyqtSignal(list, QPoint)

    def encodingValue(self):
        return self.document.encoding

    def sizeValue(self):
        return get_size(self.document.filename)

    def modifiedValue(self):
        modifiedDateime = QDateTime(datetime.fromtimestamp(os.path.getmtime(self.document.filename)))
        strDateTime = modifiedDateime.toString(Qt.SystemLocaleShortDate)
        return unicode(strDateTime)

    def linesValue(self):
        model = self.model()
        if model:
            return model.rowDataCount()
        return 0

    def columnsValue(self):
        model = self.model()
        if model:
            return model.columnDataCount();
        return 0

    def averageValue(self):
        items = len(self.selectedIndexes())
        if items>0:
            sum_ = 0.0
            for item in self.selectedIndexes():
                r = item.data().toFloat()
                if r[1]:
                    sum_ = sum_ + r[0]
                else:
                    return None
            return sum_/items
        return None

    def sumValue(self):
        okSum= False
        sum_= 0.0
        for item in self.selectedIndexes():
            r = item.data().toFloat()
            if r[1]:
                okSum= True
                sum_ = sum_ + r[0]
        if okSum:
            return sum_
        return None

    def itemsValue(self):
        return len(self.selectedIndexes())

    def setPointSize(self, pointSize):
        model = self.model()
        model.setPointSize(pointSize)

    def setSelectCell(self, row, column):
        model = self.model()
        column = column - 1
        row = row - 1
        index = model.index(row, column)
        if index.isValid():
            #1st scroll to the item
            self.scrollTo(index)
            #2st select the row & column
            self.selectRow(row)
            self.selectColumn(column)
            #3st select cell
            selectionModel = self.selectionModel()
            selectionModel.clear()
            selectionModel.select(index, QItemSelectionModel.Select)
            #focused cell
            self.setFocus()

    def search(self, text, matchMode, matchCaseOption):
        """search data in CSV"""
        result = []
        model = self.model()

        # set regular expression pattern
        if matchMode == MatchModeEnum.WholeWord:
            pattern = r'\b{0}\b'.format(str(text))
        elif matchMode == MatchModeEnum.StartsWidth:
            pattern = r'^{0}'.format(str(text))
        elif matchMode == MatchModeEnum.EndsWith:
            pattern = r'{0}$'.format(str(text))
        elif matchMode == MatchModeEnum.RegularExpression:
            pattern = r'{0}'.format(str(text))
        else:
            pattern = ''

        # compile regular expression
        if matchCaseOption:
            rePattern = re.compile(pattern, flags=re.IGNORECASE|re.DOTALL)
        else:
            rePattern = re.compile(pattern, flags=re.DOTALL)

        # search
        for numRow, dataRow in enumerate(self.document.data):
            if model.headerrow and numRow == 0:
                continue
            for numCol, dataCell in enumerate(dataRow):
                find = False
                if matchMode == MatchModeEnum.Contains:
                    if matchCaseOption:
                        find = QString(dataCell).contains(text, Qt.CaseInsensitive)
                    else:
                        find = dataCell.find(text) > -1
                else:
                    find = rePattern.search(dataCell)
                if find:
                    if model.headerrow:
                        result.append([numRow, numCol+1, dataCell])
                    else:
                        result.append([numRow+1, numCol+1, dataCell])
        return result

    def selectedIndexesToRectangularArea(self, includeHeaderRows=False):
        """convert selected indexes to string matrix"""
        result = None
        selectedIndexes = self.selectedIndexes()
        if selectedIndexes:
            # get min and max coordinates
            minColumn = selectedIndexes[0].column()
            minRow = selectedIndexes[0].row()
            maxColumn = selectedIndexes[0].column()
            maxRow = selectedIndexes[0].row()
            for selectedIndex in selectedIndexes:
                if  selectedIndex.column() < minColumn:
                    minColumn = selectedIndex.column()
                if  selectedIndex.row() < minRow:
                    minRow = selectedIndex.row()
                if  selectedIndex.column() > maxColumn:
                    maxColumn = selectedIndex.column()
                if  selectedIndex.row() > maxRow:
                    maxRow = selectedIndex.row()
            # get a two dimension matrix with default value ''
            result = []
            for _ in range(maxRow-minRow+1):
                row = ['' for _ in range(maxColumn-minColumn+1)]
                result.append(row)
            # set values in two dimension matrix
            for selectedIndex in selectedIndexes:
                column = selectedIndex.column()
                row = selectedIndex.row()
                data = selectedIndex.data()
                text = data.toString()
                result[row-minRow][column-minColumn] = text
            # add header rows
            if includeHeaderRows:
                headerRows = self._getHeaderRows()
                if headerRows:
                    header = headerRows[minColumn:maxColumn+1]
                    result.insert(0, header)
        return result

    def rectangularAreaToSelectedIndex(self, matrix):
        """paste rectangular are to selected left-upper corner"""
        selectionRanges = self.selectionModel().selection()
        if len(selectionRanges)==1:
            numRows = len(matrix)
            if numRows > 0:
                numCols = len(matrix[0])
                if numCols > 0:
                    model = self.model()
                    topLeftIndex = selectionRanges[0].topLeft()
                    selColumn = topLeftIndex.column()
                    selRow = topLeftIndex.row()
                    modelNumCols = model.columnCount()
                    modelNumRows = model.rowCount()
                    if selColumn+numCols > modelNumCols:                                       # the number of columns we have to paste, starting at the selected cell,
                        model.insertColumns(modelNumCols, numCols-(modelNumCols-selColumn))    # go beyond how many columns exist. insert the amount of columns we need
                                                                                               # to accomodate the paste


                    if selRow+numRows > modelNumRows:                                          # the number of rows we have to paste, starting at the selected cell,
                        model.insertRows(modelNumRows, numRows-(modelNumRows-selRow))          # go beyond how many rows exist. insert the amount of rows we need to
                                                                                               # accomodate the paste


                    model.blockSignals(True)     # block signals so that the "dataChanged" signal from setData doesn't
                                                 # update the view for every cell we set
                    for rowIndex, row in enumerate(matrix):
                        for colIndex, value in enumerate(row):
                            index = model.createIndex(selRow+rowIndex, selColumn+colIndex)
                            model.setData(index, QVariant(value))
                    model.blockSignals(False)    # unblock the signal and emit dataChangesd ourselves to update all
                                                 # the view at once
                    index = model.createIndex(selRow+numRows, selColumn+numCols)
                    model.dataChanged.emit(topLeftIndex, index)

    def insertRows(self, count=None):
        selectionModel = self.selectionModel()
        selectionRanges = selectionModel.selection()
        if len(selectionRanges)==1:
            model = self.model()
            topLeftIndex = selectionRanges[0].topLeft()
            bottomRightIndex = selectionRanges[0].bottomRight()
            # if top-left corner selection is inside data area
            if topLeftIndex.row() < model.rowDataCount():
                # calculate from the selection
                if count == None:
                    count = bottomRightIndex.row() - topLeftIndex.row() + 1
                # insert rows
                if count > 0:
                    model.insertRows(topLeftIndex.row(), count)
                    self.clearSelection()
                    self.selectRows(topLeftIndex.row(), count)

    def insertColumns(self, count=None):
        selectionModel = self.selectionModel()
        selectionRanges = selectionModel.selection()
        if len(selectionRanges)==1:
            model = self.model()
            topLeftIndex = selectionRanges[0].topLeft()
            bottomRightIndex = selectionRanges[0].bottomRight()
            # if top-left corner selection is inside data area
            if topLeftIndex.column() < model.columnDataCount():
                # calculate from the selection
                if count == None:
                    count = bottomRightIndex.column() - topLeftIndex.column() + 1
                # insert columns
                if count > 0:
                    model.insertColumns(topLeftIndex.column(), count)
                    self.clearSelection()
                    self.selectColumns(topLeftIndex.column(), count)
                    
    def selectRows(self, row, count):
        """Selects rows in the view"""
        model = self.model()
        rowDataCount = model.rowDataCount()
        bottomRightRow = row + count
        if bottomRightRow > rowDataCount:
            bottomRightRow = rowDataCount
        self._select(row,
                     0,
                     bottomRightRow-1,
                     model.columnDataCount()-1)

    def selectColumns(self, column, count):
        """Selects columns in the view"""
        model = self.model()
        columnDataCount = model.columnDataCount()
        bottomRightColumn = column + count
        if bottomRightColumn > columnDataCount:
            bottomRightColumn = columnDataCount
        self._select(0,
                     column,
                     model.rowDataCount()-1,
                     bottomRightColumn-1)
        
    def selectAll(self):
        """Selects all items in the view"""
        self.clearSelection()
        model = self.model()
        self._select(0,
                     0,
                     model.rowDataCount()-1,
                     model.columnDataCount()-1)

    def loadRequested(self):
        model = MyTableModel(self.document.data, config.config_headerrow)
        self.setModel(model)

    def setDocument(self, document):
        self.document = document
        self.document.loadRequested.connect(self.loadRequested)
        model = MyTableModel(self.document.data, config.config_headerrow)
        self.setModel(model)
    #
    # init
    #

    def __init__(self, document, *args):
        QTableView.__init__(self, *args)

        # config and connect scrollbars
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        verticalScrollBar = self.verticalScrollBar()
        verticalScrollBar.valueChanged.connect(self._scrollbarChangedEvent)
        horizontalScrollBar = self.horizontalScrollBar()
        horizontalScrollBar.valueChanged.connect(self._scrollbarChangedEvent)

        # set delegate
        self.setItemDelegate(QItemDataBorderDelegate())

        # set data
        self.setDocument(document)



#       self.setSortingEnabled(True)

        # table model proxy
#        proxy = StringSortModel()
#        proxy.setSourceModel(self.tablemodel)

        # tableview
#       self.setModel(self.tablemodel)#(proxy)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customContextMenuRequestedEvent)

##    def slider_value_changed(self, value):
##        print self.tablemodel.normalFontSize()
##        print value
##        self.tablemodel.setFontSize(value)
##        percent = self.tablemodel.percentFontSize()
##        self.percent.setText('{0:d}%'.format(percent))
##        #self.tablemodel.layoutChanged.emit()  # estas dos cosas # <--activa?
##        self.tableview.resizeRowsToContents()  # dan problemas.
##
##        # como seleccionar una celda de la tabla.
##        index = self.tablemodel.index(2, 2)
##        selectionModel= self.tableview.selectionModel()
##        #self.tableview.clearSelection()
##        selectionModel.clear()
##        selectionModel.select(index, QItemSelectionModel.Select)
