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

    def setPointSize(self, pointSize):
        self.pointSize = pointSize

    def rowCount(self, parent):
        if self.headerrow:
            return len(self.arraydata)-1
        else:
            return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

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
        elif role == Qt.DisplayRole:
            rowIndex = index.row()
            columnIndex = index.column()
            if self.headerrow:
                rowIndex = rowIndex + 1              
            if len(self.arraydata) > (rowIndex):
                if len(self.arraydata[rowIndex]) > columnIndex:
                    return QVariant(self.arraydata[rowIndex][columnIndex])

        return QVariant()

    def setData(self, index, value, role):
        rowIndex = index.row()
        columnIndex = index.column()
        if self.headerrow:
            rowIndex = rowIndex + 1
        if len(self.arraydata) > (rowIndex):
            if len(self.arraydata[rowIndex]) > columnIndex:
                self.arraydata[rowIndex][columnIndex] = value
        return True
    
    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
class QCsv(QTableView):

    #
    # private
    #

    def selectionChanged (self, selected, deselected):
        self.selectionChanged_.emit()
        return QTableView.selectionChanged (self, selected, deselected)

    def _customContextMenuRequestedEvent(self, point):
        if len(self.selectedIndexes()) > 0:
            self.contextMenuRequested.emit(self.selectedIndexes(), self.mapToGlobal(point))

    def _getHeaderRows(self):
        result = []
        model = self.tablemodel
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
        if config.config_headerrow:
            return len(self.document.data)-1
        return len(self.document.data)

    def columnsValue(self):
        if len(self.document.data) > 0:
            return len(self.document.data[0])
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
        self.tablemodel.setPointSize(pointSize)

    def setSelectCell(self, row, column):
        model = self.tablemodel
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
        model = self.tablemodel

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

    def loadRequested(self):
        self.tablemodel = MyTableModel(self.document.data, config.config_headerrow)
        self.setModel(self.tablemodel)

    def setDocument(self, document):
        self.document = document
        self.document.loadRequested.connect(self.loadRequested)
        self.tablemodel = MyTableModel(self.document.data, config.config_headerrow)
        self.setModel(self.tablemodel)
    #
    # init
    #

    def __init__(self, document, *args):
        QTableView.__init__(self, *args)
#        self.setSortingEnabled(True)

        # set data
        self.setDocument(document)
#       self.filename = filename
#        self.data = data

        # table model
#        self.tablemodel = MyTableModel(self.data, config.config_headerrow)

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
