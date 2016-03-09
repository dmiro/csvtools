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


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerrow=False, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.headerrow= headerrow
        self.arraydata= datain
        self.pointSize= QFont().pointSize()
        self.columnCorner = 0
        self.rowCorner = 0

    def setRowCorner(self, value):
       self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
       self.rowCorner = value
       self.endInsertRows()

    def setColumnCorner(self, value):
       self.beginInsertColumns(QModelIndex(), self.columnCount(), self.columnCount())
       self.columnCorner = value
       self.endInsertColumns()
       
    def setPointSize(self, pointSize):
        self.pointSize = pointSize
        
    def rowDataCount(self, parent=QModelIndex()):
        if self.headerrow:
            return len(self.arraydata)-1
        else:
            return len(self.arraydata)

    def columnDataCount(self, parent=QModelIndex()):
        return len(self.arraydata[0])
    
    def rowCount(self, parent=QModelIndex()):
        row = self.rowCorner + 500
        if row < self.rowDataCount():
            return self.rowDataCount()
        return row

    def columnCount(self, parent=QModelIndex()):
        column = self.columnCorner + 500
        if column < self.columnDataCount():
            return self.columnDataCount()
        return column

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
            self.arraydata[rowIndex][columnIndex] = str(value.toString())
            # emit data changed
            bottomRight = self.createIndex(self.rowCount(), self.columnCount())
            self.dataChanged.emit(index, bottomRight)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRows(self, row, count, parent = QModelIndex()):
        self.beginInsertRows(parent, row, row+count)
        for i in xrange(count):
            self.arraydata.insert(row,[])
        self.endInsertRows()
        topLeft = self.createIndex(row, 0)
        bottomRight = self.createIndex(self.rowCount(), self.columnCount())
        return True

    def insertRow (self, row, parent = QModelIndex()):
        return self.insertRows(row, 1, parent)

class QCsv(QTableView):

    #
    # private
    #

    # http://stackoverflow.com/questions/11352523/qt-and-pyqt-tablewidget-growing-row-count
    # http://stackoverflow.com/questions/19993898/dynamically-add-data-to-qtableview
    # http://permalink.gmane.org/gmane.comp.python.pyqt-pykde/25792
    def scrollbarChangedEvent(self, val):
        indexCorner = self.indexAt(QPoint(1,1))
        print 'column', indexCorner.column()
        print 'row', indexCorner.row()
        model = self.model()
        model.setColumnCorner(indexCorner.column())
        model.setRowCorner(indexCorner.row())
        print 'rowcount', model.rowCount()
        print 'columncount', model.columnCount()
        
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
            result.append(str(data.toString()))
        return result

    #
    # public
    #

    selectionChanged_ = pyqtSignal()
    contextMenuRequested = pyqtSignal(list, QPoint)

    def sizeValue(self):
        return get_size(self.document.filename)

    def modifiedValue(self):
        modifiedDateime = QDateTime(datetime.fromtimestamp(os.path.getmtime(self.document.filename)))
        strDateTime = modifiedDateime.toString(Qt.SystemLocaleShortDate)
        return unicode(strDateTime)

    def linesValue(self):
        model = self.model()
        if model:
            return model.columnDataCount()
        return 0

    def columnsValue(self):
        model = self.model()
        if model:
            return model.rowDataCount();
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
                text = str(data.toString())
                result[row-minRow][column-minColumn] = text
            # add header rows
            if includeHeaderRows:
                headerRows = self._getHeaderRows()
                if headerRows:
                    header = headerRows[minColumn:maxColumn+1]
                    result.insert(0, header)
        return result

    def rectangularAreaToSelectedIndex(self, matrix):
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
        
        vBar = self.verticalScrollBar()
        vBar.valueChanged.connect(self.scrollbarChangedEvent)
        hBar = self.horizontalScrollBar()
        hBar.valueChanged.connect(self.scrollbarChangedEvent)

#        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel) #?

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
