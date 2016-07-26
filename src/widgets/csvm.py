# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.config import config
import lib.helper as helper
import lib.enums as enums
import lib.exports
import lib.imports
import lib.images_rc
from widgets.qradiobuttondialog import QRadioButtonDialog
from lib.pointsizes import Pointsizes
import os

##class NumberSortModel(QSortFilterProxyModel):
##    def lessThan(self, left, right):
##        lvalue = left.data().toDouble()[0]
##        rvalue = right.data().toDouble()[0]
##        return lvalue < rvalue


##class StringSortModel(QSortFilterProxyModel):
##    def lessThan(self, left, right):
##        lvalue = left.data().toString().toUpper()
##        rvalue = right.data().toString().toUpper()
##        return lvalue < rvalue


##class MyTableView(QTableView):
##    def __init__(self, average, items, sum_, parent = None, *args):
##        QTableView.__init__(self, parent, *args)
##        self.average = average
##        self.items = items
##        self.sum_ = sum_
##        self.setSortingEnabled(True)

#
# class QItemDataBorderDelegate
#

class QItemDataBorderDelegate(QStyledItemDelegate):
    def __init__ (self, parent = None):
        super(QItemDataBorderDelegate, self).__init__(parent)

    def _drawLinesBorderSelectionRanges(self, index):
        tableView = self.parent()
        if tableView:
            lastSelectionRanges = tableView.lastSelectionRanges
            if lastSelectionRanges:
                rowIndex = index.row()
                columnIndex = index.column()
                for lastSelectionRange in lastSelectionRanges:
                    drawLeft = (columnIndex == lastSelectionRange.topLeft().column() and
                                rowIndex >= lastSelectionRange.topLeft().row() and
                                rowIndex <= lastSelectionRange.bottomRight().row())
                    drawRight = (columnIndex == lastSelectionRange.bottomRight().column() and
                                rowIndex >= lastSelectionRange.topLeft().row() and
                                rowIndex <= lastSelectionRange.bottomRight().row())
                    drawTop = (rowIndex == lastSelectionRange.topLeft().row() and
                                columnIndex >= lastSelectionRange.topLeft().column() and
                                columnIndex <= lastSelectionRange.bottomRight().column())
                    drawBottom = (rowIndex == lastSelectionRange.bottomRight().row() and
                                columnIndex >= lastSelectionRange.topLeft().column() and
                                columnIndex <= lastSelectionRange.bottomRight().column())
                    if drawLeft or drawRight or drawTop or drawBottom:
                        return drawLeft, drawRight, drawTop, drawBottom
        return False, False, False, False

    def paint(self, painter, option, index):
        if index:
            model = index.model()
            if model:
                # set border data area
                if config.view_showborderdata:
                    rowIndex = index.row()
                    columnIndex = index.column()
                    columnDataCount = model.columnDataCount()-1
                    rowDataCount = model.rowDataCount()-1
                    borderColor = QColor(config.view_colorborderdata)
                    borderWith = config.view_widthborderdata
                    if (rowDataCount == rowIndex) and (columnIndex <= columnDataCount):
                        painter.setPen(QPen(borderColor, borderWith, style=Qt.DotLine))
                        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
                    if (columnDataCount == columnIndex) and (rowIndex <= rowDataCount):
                        painter.setPen(QPen(borderColor, borderWith, style=Qt.DotLine))
                        painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
                # set border 'copy to clipboard'
                drawLeft, drawRight, drawTop, drawBottom = self._drawLinesBorderSelectionRanges(index)
                tableView = self.parent()
                pen = QPen(Qt.gray, 3, style=Qt.DashLine)
                pen.setDashOffset(tableView.lastSelectionRangesDashOffset)
                painter.setPen(pen)
                if drawLeft:
                    painter.drawLine(option.rect.bottomLeft(), option.rect.topLeft())
                if drawRight:
                    painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
                if drawTop:
                    painter.drawLine(option.rect.topLeft(), option.rect.topRight())
                if drawBottom:
                    painter.drawLine(option.rect.bottomRight(), option.rect.bottomLeft())
        return super(QItemDataBorderDelegate, self).paint(painter, option, index)

#
# class QCsvModel
#

class QCsvModel(QAbstractTableModel):

    #
    # init
    #

    def __init__(self, document, headerRow=False, parent=None, *args):
        super(QCsvModel, self).__init__(parent, *args)
        self.__headerRow = headerRow
        self.document = document
        self.setPointSize(Pointsizes.normal())
        self.columnCorner = 0
        self.rowCorner = 0

    #
    # public
    #

    def setHeaderRow(self, value):
        self.__headerRow = value

    def headerRow(self):
        return self.__headerRow

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

    def setPointSize(self, value):
        """set font size"""
        self.__pointSize = value
        self.__fontSize = Pointsizes.toFontSize(value)

    def pointSize(self):
        return self.__pointSize

    def rowDataCount(self, parent=QModelIndex()):
        """get row count real data"""
        return self.document.rowCount()

    def columnDataCount(self, parent=QModelIndex()):
        """get column count real data"""
        return self.document.columnCount()

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

    def dataChangedEmit(self):
        topLeftIndex = self.createIndex(self.rowCorner, self.columnCorner)
        bottomRightIndex = self.createIndex(self.rowCorner + self.rowCount(),
                                            self.columnCorner + self.columnCount())
        self.dataChanged.emit(topLeftIndex, bottomRightIndex)
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnDataCount() - 1)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self.__headerRow and role == Qt.DisplayRole and orientation == Qt.Horizontal:
            value = self.document.value(0, section)
            if config.view_showColumnNumberHeaderRow:
                title = u'{0}\n{1}'.format(section + 1, value)
                return QVariant(QString(title))
            elif value:
                return QVariant(QString(value))
        elif role == Qt.FontRole:
            font = QFont()
            font.setPointSize(self.__fontSize)
            return font
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        # return cell format
        elif role == Qt.FontRole:
            #return QFont('Courier New', 6, QFont.Bold);
            #return QFont('Courier New', self.size, QFont.Bold);
            font = QFont()
            font.setPointSize(self.__fontSize)
            return font
        # return cell value
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            rowIndex = index.row()
            columnIndex = index.column()
            return self.document.value(rowIndex, columnIndex)
        # return highlight cells that are part of the header row
        elif role == Qt.BackgroundRole and self.__headerRow:
            rowIndex = index.row()
            columnIndex = index.column()
            if rowIndex == 0 and columnIndex < self.columnDataCount():
                return QBrush(QColor(255, 255, 0, 16))
#        elif role == Qt.BackgroundRole:
#            return QBrush(QColor(8, 8, 8, 8))
##        elif role == Qt.BackgroundRole:
##            rowIndex = index.row()
##            columnIndex = index.column()
##            if self.rowDataCount() > rowIndex:
##                if self.columnDataCount() > columnIndex:
##                    return QBrush(QColor(8, 8, 8, 8))
        ###return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            # calculate row and column index
            rowIndex = index.row()
            columnIndex = index.column()
            # set data
            selection = QItemSelection(index, index)
            self.document.setValue(rowIndex, columnIndex, value.toString(), selection, selection)
            # emit data changed
            bottomRight = self.createIndex(self.rowCount(), self.columnCount())
            self.dataChanged.emit(index, bottomRight)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

##    def insertRows(self, row, count, parent = QModelIndex()):
##        self.beginInsertRows(parent, row, row+count)
##        self.document.insertEmptyRows(row, count)
##        self.endInsertRows()
##        return True

##    def insertRow(self, row, parent = QModelIndex()):
##        return self.insertRows(row, 1, parent)

##    def insertColumns(self, column, count, parent = QModelIndex()):
##        self.beginInsertColumns(parent, column, column+count)
##        self.document.insertEmptyColumns(column, count)
##        self.endInsertColumns()
##        return True

##    def insertColumn(self, column, parent = QModelIndex()):
##        return self.insertColumn(column, 1, parent)

#
# class QCsv
#

class QCsv(QTableView):

    #
    # private
    #

    def _setMenuDisabled(self, menu, disabled):
        for action in menu.actions():
            if not action.menu():
                action.setDisabled(disabled)

    def _setEditMenuDisabled(self, disabled):
        pass
        # falta repasar, ¿hace falta? si es así, evaluar cada opcion del menu.
        #self._setMenuDisabled(self._editMenu, disabled)
        #self._setMenuDisabled(self.copySpecialMenu, disabled)
        #self._setMenuDisabled(self.copyToPythonMenu, disabled)

    def _getCurrentSelection(self):
        selectionModel = self.selectionModel()
        return selectionModel.selection()

    def _getNewSelection(self, topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn):
        model = self.model()
        topLeft = model.createIndex(topLeftRow, topLeftColumn)
        bottomRight = model.createIndex(bottomRightRow, bottomRightColumn)
        return QItemSelection(topLeft, bottomRight)

    def __getDataSelection(self):
        """
        Get detailed information about selection ranges and returns an anonymous info class with data info.
        #
        hasData:            true if there are one or more selections
        isSingleSelection:  true if has data and single select range exist
        isInnerSingleSelection:true if single select range exist and entire selection is inside data area
        isMultipleSelection:true if there are multiple selection
        #
        topLeftIndex:       top-left index of the first range selection
        bottomRightIndex:   bottom-right index of the first range selection
        dimRows:            row dimension of the first range selection
        dimColumns:         column dimension of the first range selection
        #
        minTopLeftIndex:    top-left index of the min coordinate from selected indexes
        maxBottomRightIndex:bottom-right index of the min coordinate from selected indexes
        minMaxDimRows:      row dimension of the selected indexes
        minMaxDimColumns:   column dimension of the selected indexes
        minRow:             top-left row of the min coordinate from selected indexes
        minColumn:          top-left column of the min coordinate from selected indexes
        maxRow:             bottom-right row of the min coordinate from selected indexes
        maxcolumn:          bottom-right column of the min coordinate from selected indexes
        #
        selectedRanges:     selected ranges collection
        selectedIndexes:    selected indexes collection
        """
        selectedRanges = self._getCurrentSelection()
        selectedIndexes = selectedRanges.indexes()
        lenSelectedRanges = len(selectedRanges)
        if lenSelectedRanges > 0:
            topLeftIndex = selectedRanges[0].topLeft()
            bottomRightIndex = selectedRanges[0].bottomRight()
            if lenSelectedRanges == 1:
                isInnerSingleSelection =  (topLeftIndex.row() < self.document.rowCount()) and (topLeftIndex.column() < self.document.columnCount())
                return helper.SimpleNamespace(hasData = True,
                                              isSingleSelection = True,
                                              isInnerSingleSelection = isInnerSingleSelection,
                                              isMultipleSelection = False,
                                              topLeftIndex = topLeftIndex,
                                              bottomRightIndex = bottomRightIndex,
                                              dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1,
                                              dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1,
                                              minTopLeftIndex = topLeftIndex,
                                              maxBottomRightIndex = bottomRightIndex,
                                              minMaxDimRows = bottomRightIndex.row() - topLeftIndex.row() + 1,
                                              minMaxDimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1,
                                              minRow = topLeftIndex.row(),
                                              minColumn = topLeftIndex.column(),
                                              maxRow = bottomRightIndex.row(),
                                              maxColumn = bottomRightIndex.column(),
                                              selectedRanges = selectedRanges,
                                              selectedIndexes = selectedIndexes)
            else:
                model = self.model()
                minTopLeftIndex = model.createIndex(min([index.row() for index in selectedIndexes]),
                                                    min([index.column() for index in selectedIndexes]))
                maxBottomRightIndex = model.createIndex(max([index.row() for index in selectedIndexes]),
                                                        max([index.column() for index in selectedIndexes]))
                return helper.SimpleNamespace(hasData = True,
                                              isSingleSelection = False,
                                              isInnerSingleSelection = False,
                                              isMultipleSelection = True,
                                              topLeftIndex = topLeftIndex,
                                              bottomRightIndex = bottomRightIndex,
                                              dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1,
                                              dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1,
                                              minTopLeftIndex = minTopLeftIndex,
                                              maxBottomRightIndex = maxBottomRightIndex,
                                              minMaxDimRows = maxBottomRightIndex.row() - minTopLeftIndex.row() + 1,
                                              minMaxDimColumns = maxBottomRightIndex.column() - minTopLeftIndex.column() + 1,
                                              minRow = minTopLeftIndex.row(),
                                              minColumn = minTopLeftIndex.column(),
                                              maxRow = maxBottomRightIndex.row(),
                                              maxColumn = maxBottomRightIndex.column(),
                                              selectedRanges = selectedRanges,
                                              selectedIndexes = selectedIndexes)
        return helper.SimpleNamespace(hasData = False,
                                      isSingleSelection = False,
                                      isInnerSingleSelection = False,
                                      isMultipleSelection = False,
                                      topLeftIndex = None,
                                      bottomRightIndex = None,
                                      dimRows = 0,
                                      dimColumns = 0,
                                      minTopLeftIndex = None,
                                      maxBottomRightIndex = None,
                                      minMaxDimRows = 0,
                                      minMaxDimColumns = 0,
                                      minRow = 0,
                                      minColumn = 0,
                                      maxRow = 0,
                                      maxColumn = 0,
                                      selectedRanges = None,
                                      selectedIndexes = None)

    def _select(self, topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn):
        # create item selection
        model = self.model()
        topLeft = model.createIndex(topLeftRow, topLeftColumn)
        bottomRight = model.createIndex(bottomRightRow, bottomRightColumn)
        selection = QItemSelection(topLeft, bottomRight)
        # select items
        selectionModel = self.selectionModel()
        selectionModel.select(selection, QItemSelectionModel.Select)

    def _setSelection(self, selection=None):
        model = self.model()
        model.dataChangedEmit()
        self.clearSelection()
        if selection != None:
            if len(selection) > 0:
                self.setCurrentIndex(selection[0].topLeft())
                selectionModel = self.selectionModel()
                selectionModel.select(selection, QItemSelectionModel.Select)

    @helper.waiting
    def _insertEmptyArray(self, insert=enums.InsertDirectionEnum.TopInsert):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            if dimRows > 0 and dimColumns > 0:
                startRow = selection.topLeftIndex.row()
                startColumn = selection.topLeftIndex.column()
                undoSelection = self._getCurrentSelection()
                if insert == enums.InsertDirectionEnum.TopInsert:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.insertEmptyCellsInRows(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                if insert == enums.InsertDirectionEnum.BottomInsert:
                    startRow = startRow + dimRows
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.insertEmptyCellsInRows(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                if insert == enums.InsertDirectionEnum.LeftInsert:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.insertEmptyCellsInColumns(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                if insert == enums.InsertDirectionEnum.RightInsert:
                    startColumn = startColumn + dimColumns
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.insertEmptyCellsInColumns(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _removeArray(self, remove=enums.RemoveDirectionEnum.MoveLeftRemove):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            if dimRows > 0 and dimColumns > 0:
                startRow = selection.topLeftIndex.row()
                startColumn = selection.topLeftIndex.column()
                undoSelection = self._getCurrentSelection()
                if remove == enums.MoveDirectionEnum.LeftMove:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.removeArrayInRows(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                if remove==enums.RemoveDirectionEnum.MoveLeftRemove:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows - 1, startColumn + dimColumns - 1)
                    self.document.removeArrayInColumns(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _moveArray(self, move):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            if dimRows > 0 and dimColumns > 0:
                startRow = selection.topLeftIndex.row()
                startColumn = selection.topLeftIndex.column()
                undoSelection = self._getCurrentSelection()
                if move == enums.MoveDirectionEnum.LeftMove:
                    destRow = startRow
                    destColumn = startColumn - 1
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInColumns(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.RightMove:
                    destRow = startRow
                    destColumn = startColumn + 1
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInColumns(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.TopMove:
                    destRow = startRow - 1
                    destColumn = startColumn
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInRows(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.BottomMove:
                    destRow = startRow + 1
                    destColumn = startColumn
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInRows(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _mergeRows(self):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimRows
            startRow = selection.topLeftIndex.row()
            # ok
            if count > 1:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      selection.topLeftIndex.column(),
                                                      selection.topLeftIndex.row(),
                                                      selection.bottomRightIndex.column())
                self.document.mergeRows(startRow, count, None, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _mergeColumns(self):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimColumns
            startColumn = selection.topLeftIndex.column()
            # ok
            if count > 1:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      selection.topLeftIndex.column(),
                                                      selection.bottomRightIndex.row(),
                                                      selection.topLeftIndex.column())
                self.document.mergeColumns(startColumn, count, None, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _mergeArray(self, merge):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            startRow = selection.topLeftIndex.row()
            startColumn = selection.topLeftIndex.column()
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            # ok
            if dimRows > 0 and dimColumns > 0:
                undoSelection = self._getCurrentSelection()
                if merge==enums.MergeDirectionEnum.MoveLeftRemove:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows -1, startColumn)
                    self.document.mergeArrayInColumns(startRow, startColumn, dimRows, dimColumns, None, undoSelection, redoSelection)
                else:
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow, startColumn + dimColumns - 1)
                    self.document.mergeArrayInRows(startRow, startColumn, dimRows, dimColumns, None, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _insertRows(self, insert=enums.InsertBlockDirectionEnum.BeforeInsert):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimRows
            if insert == enums.InsertBlockDirectionEnum.AfterInsert:
                startRow = selection.topLeftIndex.row() + count
            else:
                startRow = selection.topLeftIndex.row()
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(startRow,
                                                      selection.topLeftIndex.column(),
                                                      startRow + count - 1,
                                                      selection.bottomRightIndex.column())
                self.document.insertEmptyRows(startRow, count, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _insertColumns(self, insert=enums.InsertBlockDirectionEnum.BeforeInsert):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimColumns
            if insert == enums.InsertBlockDirectionEnum.AfterInsert:
                startColumn = selection.topLeftIndex.column() + count
            else:
                startColumn = selection.topLeftIndex.column()
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      startColumn,
                                                      selection.bottomRightIndex.row(),
                                                      startColumn + count - 1)
                self.document.insertEmptyColumns(startColumn, count, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _removeRows(self):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            startRow = selection.topLeftIndex.row()
            count = selection.dimRows
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      selection.topLeftIndex.column(),
                                                      selection.bottomRightIndex.row(),
                                                      selection.bottomRightIndex.column())
                self.document.removeRows(startRow, count, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _removeColumns(self):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            startColumn = selection.topLeftIndex.column()
            count = selection.dimColumns
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      selection.topLeftIndex.column(),
                                                      selection.bottomRightIndex.row(),
                                                      selection.bottomRightIndex.column())
                self.document.removeColumns(startColumn, count, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _moveRows(self, move=enums.MoveBlockDirectionEnum.AfterMove):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimRows
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                if move == enums.MoveBlockDirectionEnum.BeforeMove:
                    startRow = selection.topLeftIndex.row()
                    destinationRow = startRow - 1
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row() - 1,
                                                          selection.topLeftIndex.column(),
                                                          selection.bottomRightIndex.row() - 1,
                                                          selection.bottomRightIndex.column())
                else:
                    startRow = selection.topLeftIndex.row()
                    destinationRow = startRow + 1
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row() + 1,
                                                          selection.topLeftIndex.column(),
                                                          selection.bottomRightIndex.row() + 1,
                                                          selection.bottomRightIndex.column())
                self.document.moveRows(startRow, count, destinationRow, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _moveColumns(self, move=enums.MoveBlockDirectionEnum.AfterMove):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            count = selection.dimColumns
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                if move == enums.MoveBlockDirectionEnum.BeforeMove:
                    startColumn = selection.topLeftIndex.column()
                    destinationColumn = startColumn - 1
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                          selection.topLeftIndex.column() - 1,
                                                          selection.bottomRightIndex.row(),
                                                          selection.bottomRightIndex.column() - 1)
                else:
                    startColumn = selection.topLeftIndex.column()
                    destinationColumn = startColumn + 1
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                          selection.topLeftIndex.column() + 1,
                                                          selection.bottomRightIndex.row(),
                                                          selection.bottomRightIndex.column() + 1)
                self.document.moveColumns(startColumn, count, destinationColumn, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _deleteCells(self, dataSelection=None):
        if dataSelection == None:
            dataSelection = self.__getDataSelection()
        if dataSelection.hasData:
            undoSelection = self._getCurrentSelection()
            redoSelection = self._getCurrentSelection()
            mergeId = id(redoSelection)
            with self.document.macro('delete {} cells'.format(len(dataSelection.selectedIndexes))) as macro:
                for selectedRange in dataSelection.selectedRanges:
                    topLeftIndex = selectedRange.topLeft()
                    bottomRightIndex = selectedRange.bottomRight()
                    startRow = topLeftIndex.row()
                    startColumn = topLeftIndex.column()
                    dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1
                    dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1
                    macro.deleteCells(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
            self._setSelection(redoSelection)

    @helper.waiting
    def _rectangularAreaToSelectedIndex(self, array):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            # ok
            if dimRows > 0 and dimColumns > 0:
                startRow = selection.topLeftIndex.row()
                startColumn = selection.topLeftIndex.column()
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getCurrentSelection()
                self.document.setArrayRepeater(startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _deleteCellsAndRectangularAreaToSelectedIndex(self, deleteSelection, array):
        selection = self.__getDataSelection()
        if selection.isSingleSelection:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            # ok
            if dimRows > 0 and dimColumns > 0:
                if deleteSelection.hasData:
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getCurrentSelection()
                    mergeId = id(redoSelection)
                    with self.document.macro('cut&paste {} cells'.format(len(deleteSelection.selectedIndexes))) as macro:
                        # delete
                        for selectedRange in deleteSelection.selectedRanges:
                            topLeftIndex = selectedRange.topLeft()
                            bottomRightIndex = selectedRange.bottomRight()
                            startRow = topLeftIndex.row()
                            startColumn = topLeftIndex.column()
                            dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1
                            dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1
                            macro.deleteCells(startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
                        # copy
                        startRow = selection.topLeftIndex.row()
                        startColumn = selection.topLeftIndex.column()
                        undoSelection = self._getCurrentSelection()
                        redoSelection = self._getCurrentSelection()
                        macro.setArrayRepeater(startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection)
                    self._setSelection(redoSelection)

    @helper.waiting
    def _selectedIndexesToRectangularArea(self, includeHeaderRows=False):
        """copy and convert selected indexes to string matrix
        """
        selection = self.__getDataSelection()
        if selection.hasData:
            # get a two dimension matrix with default value ''
            result = []
            for _ in range(selection.minMaxDimRows):
                row = [QString('')] * selection.minMaxDimColumns
                result.append(row)
            # set values in two dimension matrix
            for selectedIndex in selection.selectedIndexes:
                row = selectedIndex.row()
                column = selectedIndex.column()
                result[row - selection.minRow][column - selection.minColumn] = self.document.value(row, column)
            # add header rows
            if includeHeaderRows:
                row = [QString('')] * selection.minMaxDimColumns
                result.insert(0, row)
                for selectedIndex in selection.selectedIndexes:
                    column = selectedIndex.column()
                    data = self.document.value(0, column)
                    if not data:
                        data = QString(str(column + 1))
                    result[0][column - selection.minColumn] = data
            return result
        else:
            return None

    def _globalCut(self):
        QCsv._cuteDataSelection = self.__getDataSelection()
        QCsv._cuteInstance = self

    @staticmethod
    def _globalPaste():
        clipboard = QApplication.clipboard()
        if clipboard.ownsClipboard():
            if hasattr(QCsv, '_cuteDataSelection') and hasattr(QCsv, '_cuteInstance'):
                if QCsv._cuteDataSelection:
                    QCsv._cuteInstance._deleteCells(QCsv._cuteDataSelection)
                    QCsv._cuteInstance.cancelClipboardAction.trigger()
                    QCsv._cuteDataSelection = None
                    QCsv._cuteInstance = None
        return

    def _editAction(self, action):
        textClip = None

        # copy or cut to clipboard action
        if action == self.copyToClipboard or action == self.cuteToClipboard:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=False)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toClipboard(matrix)
                # set clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
                # update last selection range
                self.lastSelectionRanges = self.selectionModel().selection()
                # updates the area occupied by the given indexes in selection
                for index in self.lastSelectionRanges.indexes():
                    self.update(index)
                # if cut action then set selected indexes
                if action == self.cuteToClipboard:
                    self._globalCut()
            return

        # copy with Column Name(s) action
        if action == self.copyWithHeaderColumnsToClipboard:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toClipboard(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy Column Name(s) action
        elif action == self.copyHeaderColumnsToClipboard:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toClipboard([matrix[0]])
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy As JSON action
        elif action == self.copyAsJSON:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toJSON(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy As Delimited action
        elif action == self.copyAsDelimited:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toDelimitied(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy As Delimited action
        elif action == self.copyAsXML:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toXML(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy As Text action
        elif action == self.copyAsText:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toText(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy As HTML action
        elif action == self.copyAsHTML:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toHTML(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy Python Source Code As TEXT action
        elif action == self.copyPythonAsText:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonText(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy Python Source Code As TUPLE action
        elif action == self.copyPythonAsTuple:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonTuple(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy Python Source Code As LIST action
        elif action == self.copyPythonAsList:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonList(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # copy Python Source Code As DICT action
        elif action == self.copyPythonAsDict:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonDict(matrix)
                # copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # paste from clipboard action
        if action == self.pasteFromClipboard:
            clipboard = QApplication.clipboard()
            textClip = clipboard.text()
            matrix = lib.imports.ClipboardFormat.toMatrix(textClip)
            # cute and paste in same instance
            if hasattr(QCsv, '_cuteDataSelection') and hasattr(QCsv, '_cuteInstance'):
                if QCsv._cuteInstance == self:
                    self._deleteCellsAndRectangularAreaToSelectedIndex(QCsv._cuteDataSelection, matrix)
                    QCsv._cuteInstance.cancelClipboardAction.trigger()
                    QCsv._cuteDataSelection = None
                    QCsv._cuteInstance = None
                    return
            # cute and paste in diff instances
            self._globalPaste()
            self._rectangularAreaToSelectedIndex(matrix)
            return

        # insert column to the left
        if action == self.insertColumnLeftAction or \
           action == self.insertColumnAction:
            self._insertColumns(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            return

        # insert column to the right
        if action == self.insertColumnRightAction:
            self._insertColumns(insert=enums.InsertBlockDirectionEnum.AfterInsert)
            return

        # insert row to the top
        if action == self.insertRowTopAction or \
           action == self.insertRowAction:
            self._insertRows(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            return

        # insert row to the bottom
        if action == self.insertRowBottomAction:
            self._insertRows(insert=enums.InsertBlockDirectionEnum.AfterInsert)
            return

        # remove rows
        if action == self.removeRowsAction:
            self._removeRows()
            return

        # merge rows
        if action == self.mergeRowsAction:
            self._mergeRows()
            return

        # remove columns
        if action == self.removeColumnsAction:
            self._removeColumns()
            return

        # merge columns
        if action == self.mergeColumnsAction:
            self._mergeColumns()
            return

        # insert edit
        if action == self.insertEdit:
            option = QRadioButtonDialog.getSelectItem('Insert',
                                                      ['Shift cells right',
                                                       'Shift cells down',
                                                       'Insert an entire row',
                                                       'Insert an entire column'],
                                                      parent=self)
            if option == 0:
                self._insertEmptyArray(insert=enums.InsertDirectionEnum.LeftInsert)
            if option == 1:
                self._insertEmptyArray(insert=enums.InsertDirectionEnum.TopInsert)
            if option == 2:
                self._insertRows(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            if option == 3:
                self._insertColumns(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            return

        # remove edit
        if action == self.removeEdit:
            option = QRadioButtonDialog.getSelectItem('Remove',
                                                      ['Shift cells left',
                                                       'Shift cells up',
                                                       'Remove entire row',
                                                       'Remove entire column'],
                                                      parent=self)
            if option == 0:
                self._removeArray(remove=enums.RemoveDirectionEnum.MoveLeftRemove)
            if option == 1:
                self._removeArray(remove=enums.RemoveDirectionEnum.MoveUpRemove)
            if option == 2:
                self._removeRows()
            if option == 3:
                self._removeColumns()
            return

        # merge edit
        if action == self.mergeEdit:
            option = QRadioButtonDialog.getSelectItem('Merge',
                                                      ['Shift cells left',
                                                       'Shift cells up',
                                                       'Merge entire row',
                                                       'Merge entire column'],
                                                      parent=self)
            if option == 0:
                self._mergeArray(merge=enums.MergeDirectionEnum.MoveLeftRemove)
            if option == 1:
                self._mergeArray(merge=enums.MergeDirectionEnum.MoveUpRemove)
            if option == 2:
                self._mergeRows()
            if option == 3:
                self._mergeColumns()
            return

        # move row to the top
        if action == self.moveRowTopAction:
            self._moveRows(move=enums.MoveBlockDirectionEnum.BeforeMove)
            return

        # move row to the bottom
        if action == self.moveRowBottomAction:
            self._moveRows(move=enums.MoveBlockDirectionEnum.AfterMove)
            return

        # move column to the left
        if action == self.moveColumnLeftAction:
            self._moveColumns(move=enums.MoveBlockDirectionEnum.BeforeMove)
            return

        # move column to the right
        if action == self.moveColumnRightAction:
            self._moveColumns(move=enums.MoveBlockDirectionEnum.AfterMove)
            return

        # move cell to the left
        if action == self.moveCellLeftAction:
            self._moveArray(move=enums.MoveDirectionEnum.LeftMove)
            return

        # move cell to the right
        if action == self.moveCellRightAction:
            self._moveArray(move=enums.MoveDirectionEnum.RightMove)
            return

        # move cell to the top
        if action == self.moveCellTopAction:
            self._moveArray(move=enums.MoveDirectionEnum.TopMove)
            return

        # move cell to the bottom
        if action == self.moveCellBottomAction:
            self._moveArray(move=enums.MoveDirectionEnum.BottomMove)
            return

        # remove cell and up
        if action ==  self.removeCellMoveUpAction:
            self._removeArray(remove=enums.RemoveDirectionEnum.MoveUpRemove)
            return

        # remove cell and left
        if action == self.removeCellMoveLeftAction:
            self._removeArray(remove=enums.RemoveDirectionEnum.MoveLeftRemove)
            return

        # insert cell to the left
        if action == self.insertCellLeftAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.LeftInsert)
            return

        # insert cell to the right
        if action == self.insertCellRightAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.RightInsert)
            return

        # insert cell to the top
        if action == self.insertCellTopAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.TopInsert)
            return

        # insert cell to the bottom
        if action == self.insertCellBottomAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.BottomInsert)
            return

        # merge cells to the left
        if action == self.mergeCellsLeftAction:
            self._mergeArray(merge=enums.MergeDirectionEnum.MoveLeftRemove)
            return

        # merge cells to the top
        if action == self.mergeCellsTopAction:
            self._mergeArray(merge=enums.MergeDirectionEnum.MoveUpRemove)
            return

        # select all
        if action == self.selectAllEdit:
            self.selectAll()
            return

        # delete cells
        if action == self.deleteEdit:
            self._deleteCells()
            return

        # UNDO
        if action == self.undoEdit:
            undoSelection = self.document.undo()
            self._setSelection(undoSelection)
            return

        # REDO
        if action == self.redoEdit:
            redoSelection = self.document.redo()
            self._setSelection(redoSelection)
            return

    def _viewAction(self, action):

        # header row action
        if action == self.headerRowAction:
            model = self.model()
            model.setHeaderRow(self.headerRowAction.isChecked())

        self.refresh()

    def _addViewMenu(self):
        """add VIEW menu"""

        # view menu
        self._viewMenu = QMenu(self.tr('View'))
        self.headerRowAction = self._viewMenu.addAction(self.tr('Header Row'))
        self.headerRowAction.setCheckable(True)
        self.headerRowAction.setChecked(config.view_headerrow)

        # connect menu action
        self._viewMenu.triggered.connect(self._viewAction)

    def _addEditMenu(self):
        """add EDIT menu"""

        #
        # general edit menu
        #

        self._editMenu = QMenu(self.tr('Edit'))
        self.undoEdit = self._editMenu.addAction(QIcon(':images/undo.png'), self.tr('Undo'))
        self.undoEdit.setShortcut(QKeySequence.Undo)
        self.undoEdit.setEnabled(False)
        self.redoEdit = self._editMenu.addAction(QIcon(':images/redo.png'), self.tr('Redo'))
        self.redoEdit.setShortcut(QKeySequence.Redo)
        self.redoEdit.setEnabled(False)
        self._editMenu.addSeparator()
        self.cuteToClipboard = self._editMenu.addAction(QIcon(':images/cut.png'), self.tr('Cut'))
        self.cuteToClipboard.setShortcut(QKeySequence.Cut)
        self.copyToClipboard = self._editMenu.addAction(QIcon(':images/copy.png'), self.tr('&Copy'))
        self.copyToClipboard.setShortcut(QKeySequence.Copy)
        self.pasteFromClipboard = self._editMenu.addAction(QIcon(':images/paste.png'), self.tr('Paste'))
        self.pasteFromClipboard.setShortcut(QKeySequence.Paste)
        self.insertEdit = self._editMenu.addAction(self.tr('Insert...'))
        self.insertEdit.setShortcut('Ctrl+Ins')
        self.removeEdit = self._editMenu.addAction(self.tr('Remove...'))
        self.removeEdit.setShortcut('Ctrl+Delete')
        self.mergeEdit = self._editMenu.addAction(self.tr('Merge...'))
        self.mergeEdit.setShortcut('Ctrl+M')
        self.deleteEdit = self._editMenu.addAction(QIcon(':images/eraser.png'), self.tr('Delete content'))
        self.deleteEdit.setShortcut(QKeySequence.Delete)
        self.selectAllEdit = self._editMenu.addAction(QIcon(':images/all.png'), self.tr('Select All'))
        self.selectAllEdit.setShortcut(QKeySequence.SelectAll)
        self._editMenu.addSeparator()

        # columns submenu
        self.editColumnsMenu = self._editMenu.addMenu(self.tr('Columns'))
        self.insertColumnLeftAction = self.editColumnsMenu.addAction(QIcon(':tools/addcolumnleft.png'), self.tr('Insert left'))
        self.insertColumnLeftAction.setShortcut('Ctrl+K, Left')
        self.insertColumnRightAction = self.editColumnsMenu.addAction(QIcon(':tools/addcolumnright.png'), self.tr('Insert right'))
        self.insertColumnRightAction.setShortcut('Ctrl+K, Right')
        self.editColumnsMenu.addSeparator()
        self.moveColumnLeftAction = self.editColumnsMenu.addAction(QIcon(':tools/movecolumnleft.png'), self.tr('Move left'))
        self.moveColumnLeftAction.setShortcut('Alt+Shift+Left')
        self.moveColumnRightAction = self.editColumnsMenu.addAction(QIcon(':tools/movecolumnright.png'), self.tr('Move right'))
        self.moveColumnRightAction.setShortcut('Alt+Shift+Right')
        self.editColumnsMenu.addSeparator()
        self.removeColumnsAction = self.editColumnsMenu.addAction(QIcon(':tools/removecolumn.png'), self.tr('Remove'))
        self.mergeColumnsAction = self.editColumnsMenu.addAction(QIcon(':tools/mergecolumns.png'), self.tr('Merge'))

        # rows submenu
        self.editRowsMenu = self._editMenu.addMenu(self.tr('Rows'))
        self.insertRowTopAction = self.editRowsMenu.addAction(QIcon(':tools/addrowtop.png'), self.tr('Insert top'))
        self.insertRowTopAction.setShortcut('Ctrl+K, Up')
        self.insertRowBottomAction = self.editRowsMenu.addAction(QIcon(':tools/addrowbottom.png'), self.tr('Insert bottom'))
        self.insertRowBottomAction.setShortcut('Ctrl+K, Down')
        self.editRowsMenu.addSeparator()
        self.moveRowTopAction = self.editRowsMenu.addAction(QIcon(':tools/moverowtop.png'), self.tr('Move top'))
        self.moveRowTopAction.setShortcut('Alt+Shift+Up')
        self.moveRowBottomAction = self.editRowsMenu.addAction(QIcon(':tools/moverowbottom.png'), self.tr('Move bottom'))
        self.moveRowBottomAction.setShortcut('Alt+Shift+Down')
        self.editRowsMenu.addSeparator()
        self.removeRowsAction = self.editRowsMenu.addAction(QIcon(':tools/removerow.png'), self.tr('Remove'))
        self.mergeRowsAction = self.editRowsMenu.addAction(QIcon(':tools/mergerows.png'), self.tr('Merge'))

        # cells submenu
        self.editCellsMenu = self._editMenu.addMenu(self.tr('Cells'))
        self.insertCellLeftAction = self.editCellsMenu.addAction(QIcon(':tools/addcellleft.png'), self.tr('Insert left'))
        self.insertCellLeftAction.setShortcut('Ctrl+L, Left')
        self.insertCellRightAction = self.editCellsMenu.addAction(QIcon(':tools/addcellright.png'), self.tr('Insert right'))
        self.insertCellRightAction.setShortcut('Ctrl+L, Right')
        self.insertCellTopAction = self.editCellsMenu.addAction(QIcon(':tools/addcelltop.png'), self.tr('Insert top'))
        self.insertCellTopAction.setShortcut('Ctrl+L, Up')
        self.insertCellBottomAction = self.editCellsMenu.addAction(QIcon(':tools/addcellbottom.png'), self.tr('Insert bottom'))
        self.insertCellBottomAction.setShortcut('Ctrl+L, Down')
        self.editCellsMenu.addSeparator()
        self.moveCellLeftAction = self.editCellsMenu.addAction(QIcon(':tools/movecellleft.png'), self.tr('Move left'))
        self.moveCellLeftAction.setShortcut('Ctrl+Shift+Left')
        self.moveCellRightAction = self.editCellsMenu.addAction(QIcon(':tools/movecellright.png'), self.tr('Move right'))
        self.moveCellRightAction.setShortcut('Ctrl+Shift+Right')
        self.moveCellTopAction = self.editCellsMenu.addAction(QIcon(':tools/movecelltop.png'), self.tr('Move top'))
        self.moveCellTopAction.setShortcut('Ctrl+Shift+Up')
        self.moveCellBottomAction = self.editCellsMenu.addAction(QIcon(':tools/movecellbottom.png'), self.tr('Move bottom'))
        self.moveCellBottomAction.setShortcut('Ctrl+Shift+Down')
        self.editCellsMenu.addSeparator()
        self.removeCellMoveUpAction = self.editCellsMenu.addAction(QIcon(':tools/removecelltop.png'), self.tr('Remove and move up'))
        self.removeCellMoveLeftAction = self.editCellsMenu.addAction(QIcon(':tools/removecellleft.png'), self.tr('Remove and move to the left'))
        self.editCellsMenu.addSeparator()
        self.mergeCellsTopAction = self.editCellsMenu.addAction(QIcon(':tools/mergecellstop.png'), self.tr('Merge and move up'))
        self.mergeCellsLeftAction = self.editCellsMenu.addAction(QIcon(':tools/mergecellsleft.png'), self.tr('Merge and move to the left'))
        self._editMenu.addSeparator()

        # copy special submenu
        self.copySpecialMenu = self._editMenu.addMenu(self.tr('Copy Special'))
        self.copyToSourceCodeMenu = self._editMenu.addMenu(self.tr('Copy to Source Code'))
        self.copyToPythonMenu = self.copyToSourceCodeMenu.addMenu(self.tr('Python'))
        self.copyWithHeaderColumnsToClipboard = self.copySpecialMenu.addAction(self.tr('Copy with Column Name(s)'))
        self.copyHeaderColumnsToClipboard = self.copySpecialMenu.addAction(self.tr('Copy Column Name(s)'))
        self.copyAsText = self.copySpecialMenu.addAction(self.tr('Copy As Text'))
        self.copyAsDelimited = self.copySpecialMenu.addAction(self.tr('Copy As Delimited'))
        self.copyAsJSON = self.copySpecialMenu.addAction(self.tr('Copy As JSON'))
        self.copyAsXML = self.copySpecialMenu.addAction(self.tr('Copy As XML'))
        self.copyAsHTML = self.copySpecialMenu.addAction(self.tr('Copy As HTML'))

        # copy to Python source code sub-submenu
        self.copyPythonAsText = self.copyToPythonMenu.addAction(self.tr('As Text'))
        self.copyPythonAsTuple = self.copyToPythonMenu.addAction(self.tr('As Tuple'))
        self.copyPythonAsList = self.copyToPythonMenu.addAction(self.tr('As List'))
        self.copyPythonAsDict = self.copyToPythonMenu.addAction(self.tr('As Dict'))

        # connect menu action
        self._editMenu.triggered.connect(self._editAction)

        #### #copy to source code submenu
        #### self.copyToSourceCodeMenu.addAction(QAction('C++', self)) ## acabar
        #### self.copyToSourceCodeMenu.addAction(QAction('C#', self)) ## acabar
        #### self.copyToSourceCodeMenu.addAction(QAction('Delphi', self)) ## acabar
        #### self.copyToSourceCodeMenu.addAction(QAction('Java', self)) ## acabar
        #### self.copyToSourceCodeMenu.addAction(QAction('Python', self)) ## acabar
        #### #ideas
        #### algo del estilo llamadas RESTFUL con datos del CSV...

        #
        # horizontal edit menu
        #

        self._horizontalEditMenu = QMenu('')
        self._horizontalEditMenu.addAction(self.cuteToClipboard)
        self._horizontalEditMenu.addAction(self.copyToClipboard)
        self._horizontalEditMenu.addAction(self.pasteFromClipboard)
        self._horizontalEditMenu.addAction(self.deleteEdit)
        self._horizontalEditMenu.addSeparator()
        self.insertRowAction = self._horizontalEditMenu.addAction(QIcon(':tools/addrow.png'), self.tr('Insert'))
        self.insertRowAction.triggered[()].connect(lambda action=self.insertRowAction: self._editAction(action))
        self._horizontalEditMenu.addAction(self.removeRowsAction)
        self._horizontalEditMenu.addAction(self.mergeRowsAction)
        self._horizontalEditMenu.addAction(self.moveRowTopAction)
        self._horizontalEditMenu.addAction(self.moveRowBottomAction)

        #
        # vertical edit menu
        #

        self._verticalEditMenu = QMenu('')
        self._verticalEditMenu.addAction(self.cuteToClipboard)
        self._verticalEditMenu.addAction(self.copyToClipboard)
        self._verticalEditMenu.addAction(self.pasteFromClipboard)
        self._verticalEditMenu.addAction(self.deleteEdit)
        self._verticalEditMenu.addSeparator()
        self.insertColumnAction = self._verticalEditMenu.addAction(QIcon(':tools/addcolumn.png'), self.tr('Insert'))
        self.insertColumnAction.triggered[()].connect(lambda action=self.insertColumnAction: self._editAction(action))
        self._verticalEditMenu.addAction(self.removeColumnsAction)
        self._verticalEditMenu.addAction(self.mergeColumnsAction)
        self._verticalEditMenu.addAction(self.moveColumnLeftAction)
        self._verticalEditMenu.addAction(self.moveColumnRightAction)


    #
    # event
    #

    def _csvSelectionChangedEvent(self):
        """enable or disable menu options depending on the status"""
        numSelectedIndexes = len(self.selectedIndexes())
        self._setEditMenuDisabled(numSelectedIndexes == 0)

    def _csvcontextMenuRequestedEvent(self, selectedIndexes, globalPoint):
        """show popup edit menu"""
        self._editMenu.exec_(globalPoint)

    def _clipboardCancelEvent(self, r):
        if self.lastSelectionRanges:
            clipboard = QApplication.clipboard()
            if clipboard.ownsClipboard():
                clipboard.clear()                 # it's important to respect
                self.lastSelectionRanges = None   # this order

    def _clipboardDataChangedEvent(self):
        if self.lastSelectionRanges:
            # lastSelectionRanges to None and refresh view
            selectionRanges = self.lastSelectionRanges
            self.lastSelectionRanges = None
            # updates the area occupied by the given indexes in selection
            for index in selectionRanges.indexes():
                self.update(index)

    # http://stackoverflow.com/questions/11352523/qt-and-pyqt-tablewidget-growing-row-count
    # http://stackoverflow.com/questions/19993898/dynamically-add-data-to-qtableview
    # http://permalink.gmane.org/gmane.comp.python.pyqt-pykde/25792
    def _scrollbarChangedEvent(self, val):
        indexCorner = self.indexAt(QPoint(1,1))
        model = self.model()
        model.setColumnCorner(indexCorner.column())
        model.setRowCorner(indexCorner.row())

    def _customContextMenuRequestedEvent(self, point):
        if len(self.selectedIndexes()) > 0:
            self.contextMenuRequested.emit(self.selectedIndexes(), self.mapToGlobal(point))

    def _customContextMenuRequestedHorizontalHeaderEvent(self, point):
        globalPoint = self.mapToGlobal(point)
        self._verticalEditMenu.exec_(globalPoint)

    def _customContextMenuRequestedVerticalHeaderEvent(self, point):
        globalPoint = self.mapToGlobal(point)
        self._horizontalEditMenu.exec_(globalPoint)

    def _redoTextChanged(self, msg, enable):
        self.redoEdit.setEnabled(enable)
        self.redoEdit.setText('Redo {}'.format(msg))

    def _undoTextChanged(self, msg, enable):
        self.undoEdit.setEnabled(enable)
        self.undoEdit.setText('Undo {}'.format(msg))

    def _loadRequested(self):
        self.refresh()

    def _saveRequested(self):
        self.refresh()

    def _fileChanged(self):
        self.fileChanged.emit(self)

    #
    # override
    #

    def selectionChanged (self, selected, deselected):
        """override method 'selectionChanged' to emit my own event
        """
        self.selectionChanged_.emit(self)
        return super(QCsv, self).selectionChanged (selected, deselected)

    def timerEvent(self, timerEvent):
        """override method 'timerEvent' to give effect to the borders around the areas copied to clipboard
        """
        timerId = timerEvent.timerId()
        if self.lastSelectionRangesTimerId == timerId:
            if self.lastSelectionRanges:
                # set dash offset to get movement effect
                if self.lastSelectionRangesDashOffset > 4:
                    self.lastSelectionRangesDashOffset = 0
                else:
                    self.lastSelectionRangesDashOffset = self.lastSelectionRangesDashOffset + 1
                # updates the area occupied by the given indexes in selection
                for index in self.lastSelectionRanges.indexes():
                    self.update(index)
            return
        super(QCsv, self).timerEvent(timerEvent)

    def zoom(self, rate):
        value = self.pointSizeValue()
        value = Pointsizes.zoom(value, rate)
        self.setPointSize(value)
        self.selectionChanged_.emit(self)

    def wheelEvent (self, wheelEvent):
        """ctrl + wheel mouse = zoom in/out
        """
        if (wheelEvent.modifiers() & Qt.ControlModifier):
            # zoom out
            if wheelEvent.delta() < 0:
                self.zoom(-1)
            # zoom in
            elif wheelEvent.delta() > 0:
                self.zoom(+1)
        else:
            super(QCsv, self).wheelEvent(wheelEvent)

    #
    # public
    #

    selectionChanged_ = pyqtSignal(object)
    contextMenuRequested = pyqtSignal(list, QPoint)
    fileChanged = pyqtSignal(object)

    def hasChanges(self):
        """document has changes"""
        return self.document.hasChanges()

    def countChanges(self):
        """number of changes make to document"""
        return self.document.countChanges()

    def encodingValue(self):
        """encoding of document"""
        return self.document.encoding()

    def sizeValue(self):
        """size file in bytes of document"""
        return self.document.size()

    def modifiedValue(self):
        """last modified date and time of document"""
        return self.document.modified()

    def linesValue(self):
        """lines number of document"""
        model = self.model()
        if model:
            return model.rowDataCount()
        return 0

    def columnsValue(self):
        """columns number of document"""
        model = self.model()
        if model:
            return model.columnDataCount();
        return 0

    def averageValue(self):
        """average value of selected cells"""
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
        """sum value of selected cells"""
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
        """number of cells selected"""
        return len(self.selectedIndexes())

    def pointSizeValue(self):
        model = self.model()
        return model.pointSize()

    def refresh(self):
        model = self.model()
        model.dataChangedEmit()
        #self.resizeRowsToContents()

    def setPointSize(self, value):
        model = self.model()
        model.setPointSize(value)
        model.dataChangedEmit()
        self.resizeRowsToContents()

    def setSelectCell(self, row, column):
        model = self.model()
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
            self.setCurrentIndex(index)
            #focused cell
            self.setFocus()

    def search(self, text, matchMode, matchCaseOption):
        if self.document:
            return self.document.search(text, matchMode, matchCaseOption)

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

    def setDocument(self, document):
        self.document = document
        self.document.loadRequested.connect(self._loadRequested)
        self.document.saveRequested.connect(self._saveRequested)
        self.document.fileChanged.connect(self._fileChanged)
        self.document.redoTextChanged.connect(self._redoTextChanged)
        self.document.undoTextChanged.connect(self._undoTextChanged)
        model = QCsvModel(self.document, config.view_headerrow)
        self.setModel(model)

    def viewMenu(self):
        return self._viewMenu

    def editMenu(self):
        return self._editMenu

    def edit (self, index, trigger, event):
        """override method 'edit' to cancel area copied to the clipboard if
        the user edits inside the area"""
        editing = QTableView.edit(self, index, trigger, event)
        # view's state is now EditingState
        if editing:
            if self.lastSelectionRanges:
                if self.lastSelectionRanges.contains(index):
                    self.lastSelectionRanges = None
                    clipboard = QApplication.clipboard()
                    clipboard.clear()
        return editing

    #
    # del
    #

    def __del__(self):
        try:
            clipboard = QApplication.clipboard()
            clipboard.dataChanged.disconnect(self._clipboardDataChangedEvent)
            QCsv.cuteSelectionRanges = None
            QCsv.cuteInstance = None
            if self.document:
                self.document.loadRequested.disconnect(self._loadRequested)
                self.document.saveRequested.disconnect(self._saveRequested)
                self.document.fileChanged.disconnect(self._fileChanged)
                self.document.redoTextChanged.disconnect(self._redoTextChanged)
                self.document.undoTextChanged.disconnect(self._undoTextChanged)
        except:
            pass

    #
    # init
    #

    def __init__(self, document, *args):
        super(QCsv, self).__init__(*args)

        # config and connect scrollbars
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        verticalScrollBar = self.verticalScrollBar()
        verticalScrollBar.valueChanged.connect(self._scrollbarChangedEvent)
        horizontalScrollBar = self.horizontalScrollBar()
        horizontalScrollBar.valueChanged.connect(self._scrollbarChangedEvent)

        # set item delegate
        self.setItemDelegate(QItemDataBorderDelegate(parent=self))

        # set document
        self.setDocument(document)

        # tableview
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customContextMenuRequestedEvent)

        # tableview horizontal header
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._customContextMenuRequestedHorizontalHeaderEvent)

        # tableview horizontal header
        header = self.verticalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._customContextMenuRequestedVerticalHeaderEvent)

        # clipboard
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self._clipboardDataChangedEvent)
        self.lastSelectionRanges = None
        self.lastSelectionRangesTimerId = self.startTimer(200)
        self.lastSelectionRangesDashOffset = 0

        # cancel clipboard action
        self.cancelClipboardAction = QAction(self)
        self.cancelClipboardAction.setShortcut('ESC')
        self.cancelClipboardAction.triggered.connect(self._clipboardCancelEvent)
        self.addAction(self.cancelClipboardAction)

        # edit menu
        self._addEditMenu()
        self._addViewMenu()
        self.contextMenuRequested.connect(self._csvcontextMenuRequestedEvent)
        self.selectionChanged_.connect(self._csvSelectionChangedEvent)
