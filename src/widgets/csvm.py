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
from datetime import datetime
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

    def __init__(self, document, headerrow=False, parent=None, *args):
        super(QCsvModel, self).__init__(parent, *args)
        self.headerrow= headerrow
        self.document= document
        self.pointSize= QFont().pointSize()
        self.columnCorner = 0
        self.rowCorner = 0

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

    def setPointSize(self, pointSize):
        """set font size"""
        self.pointSize = pointSize

    def rowDataCount(self, parent=QModelIndex()):
        """get row count real data"""
    #    if self.headerrow:
    #        return self.document.rowCount() - 1
    #    else:
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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self.headerrow and role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return QVariant(self.document.value(0, section))
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
            return self.document.value(rowIndex, columnIndex)
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
            if self.headerrow:
                rowIndex = rowIndex + 1
            # set data
            self.document.setValue(rowIndex, columnIndex, value.toString())
            # emit data changed
            bottomRight = self.createIndex(self.rowCount(), self.columnCount())
            self.dataChanged.emit(index, bottomRight)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRows(self, row, count, parent = QModelIndex()):
        self.beginInsertRows(parent, row, row+count)
        self.document.insertEmptyRows(row, count)
        self.endInsertRows()
        return True

    def insertRow(self, row, parent = QModelIndex()):
        return self.insertRows(row, 1, parent)

    def insertEmptyCellsInRows(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.beginInsertRows(parent, row, row + dimRows)
        self.document.insertEmptyCellsInRows(row, column, dimRows, dimColumns)
        self.endInsertRows()
        return True

    def insertEmptyCellsInColumns(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.beginInsertColumns(parent, column, column + dimColumns)
        self.document.insertEmptyCellsInColumns(row, column, dimRows, dimColumns)
        self.endInsertColumns()
        return True

    def removeArrayInColumns(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.beginRemoveRows(parent, column, column + dimColumns)
        self.document.removeArrayInColumns(row, column, dimRows, dimColumns)
        self.endRemoveRows()
        return True

    def removeArrayInRows(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.beginRemoveRows(parent, column, column + dimColumns)
        self.document.removeArrayInRows(row, column, dimRows, dimColumns)
        self.endRemoveRows()
        return True

    def insertColumns(self, column, count, parent = QModelIndex()):
        self.beginInsertColumns(parent, column, column+count)
        self.document.insertEmptyColumns(column, count)
        self.endInsertColumns()
        return True

    def insertColumn(self, column, parent = QModelIndex()):
        return self.insertColumn(column, 1, parent)

##    def removeRows(self, row, count, parent = QModelIndex()):
##        self.beginRemoveRows(parent, row, count)
##        self.document.removeRows(row, count)
##        self.endRemoveRows()
##        return True

##    def removeRow(self, row, parent = QModelIndex()):
##        return self.removeRows(row, 1, parent)

##    def removeColumns(self, column, count, parent = QModelIndex()):
##        self.beginRemoveColumns(parent, column, count)
##        self.document.removeColumns(column, count)
##        self.endRemoveColumns()
##        return True
##
##    def removeColumn(self, column, parent = QModelIndex()):
##        return self.removeColumns(column, 1, parent)

##    def moveRows(self, sourceRow, count, destinationRow, parent = QModelIndex()):
##        self.beginInsertRows(parent, sourceRow, sourceRow+count)
##        self.document.moveRows(sourceRow, count, destinationRow)
##        self.endInsertRows()
##        return True

##    def moveRow(self, sourceRow, destinationRow, parent = QModelIndex()):
##        return self.moveRows(sourceRow, 1, destinationRow, parent)

##    def moveArrayInRows(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, parent = QModelIndex()):
##        self.beginInsertRows(parent, startRow, startRow+dimRows)
##        self.document.moveArrayInRows(startRow, startColumn, dimRows, dimColumns, destRow, destColumn)
##        self.endInsertRows()
##        return True

##    def moveColumns(self, sourceColumn, count, destinationColumn, parent = QModelIndex()):
##        self.beginInsertColumns(parent, sourceColumn, sourceColumn+count)
##        self.document.moveColumns(sourceColumn, count, destinationColumn)
##        self.endInsertColumns()
##        return True

##    def moveColumn(self, sourceColumn, destinationColumn, parent = QModelIndex()):
##        return self.moveColumns(sourceColumn, 1, destinationColumn, parent)

##    def moveArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, parent = QModelIndex()):
##        self.beginInsertColumns(parent, startColumn, startColumn+dimColumns)
##        self.document.moveArrayInColumns(startRow, startColumn, dimRows, dimColumns, destRow, destColumn)
##        self.endInsertColumns()
##        return True

    def deleteCells(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.document.deleteCells(row, column, dimRows, dimColumns)
        topLeft = self.createIndex(row, column)
        bottomRight = self.createIndex(row+dimRows, column+dimColumns)
        self.dataChanged.emit(topLeft, bottomRight)
        return True

    def mergeRows(self, startRow, rows, parent = QModelIndex()):
        self.document.mergeRows(startRow, rows)
        topLeft = self.createIndex(startRow, 0)
        bottomRight = self.createIndex(startRow+rows, self.columnCount())
        self.dataChanged.emit(topLeft, bottomRight)
        return True

    def mergeColumns(self, startColumn, columns, parent = QModelIndex()):
        self.document.mergeColumns(startColumn, columns)
        topLeft = self.createIndex(0, startColumn)
        bottomRight = self.createIndex(self.rowCount(), startColumn+columns)
        self.dataChanged.emit(topLeft, bottomRight)
        return True

    def mergeArrayInColumns(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.document.mergeArrayInColumns(row, column, dimRows, dimColumns)
        topLeft = self.createIndex(row, column)
        bottomRight = self.createIndex(row+dimRows, column+dimColumns)
        self.dataChanged.emit(topLeft, bottomRight)
        return True

    def mergeArrayInRows(self, row, column, dimRows, dimColumns, parent = QModelIndex()):
        self.document.mergeArrayInRows(row, column, dimRows, dimColumns)
        topLeft = self.createIndex(row, column)
        bottomRight = self.createIndex(row+dimRows, column+dimColumns)
        self.dataChanged.emit(topLeft, bottomRight)
        return True


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

    def selectionChanged (self, selected, deselected):
        self.selectionChanged_.emit()
        return QTableView.selectionChanged (self, selected, deselected)

    def _getHeaderRows(self):
        result = []
        model = self.model()
        columnCount = model.columnCount(None)
        for column in xrange(columnCount):
            data = model.headerData(column, orientation = Qt.Horizontal)
            result.append(data.toString())
        return result

############

    def _getCurrentSelection(self):
        selectionModel = self.selectionModel()
        return selectionModel.selection()

    def _getNewSelection(self, topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn):
        model = self.model()
        topLeft = model.createIndex(topLeftRow, topLeftColumn)
        bottomRight = model.createIndex(bottomRightRow, bottomRightColumn)
        return QItemSelection(topLeft, bottomRight)

    def _getValidSelection2(self):
        """
        selects the first SelectRange and returns an anonymous info class about it:
          isValid = True, if select range exist
          topLeftIndex
          bottomRightIndex
          dimRows
          dimColumn
        """
        selectionRanges = self._getCurrentSelection()
        if len(selectionRanges) == 1:
            topLeftIndex = selectionRanges[0].topLeft()
            bottomRightIndex = selectionRanges[0].bottomRight()
            # Is valid if top-left corner selection is inside data area
            isValid =  (topLeftIndex.row() < self.document.rowCount()) and (topLeftIndex.column() < self.document.columnCount())
            return helper.SimpleNamespace(isValid = isValid,
                                          hasData = True,
                                          topLeftIndex = topLeftIndex,
                                          bottomRightIndex = bottomRightIndex,
                                          dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1,
                                          dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1)
        return helper.SimpleNamespace(isValid = False,
                                      hasData = False,
                                      topLeftIndex = None,
                                      bottomRightIndex = None,
                                      dimRows = 0,
                                      dimColumns = 0)

    def _getValidSelection(self):
        """
        selects the first SelectRange and returns info about it:
          True, if select range exist
          topLeftIndex
          bottomRightIndex
          dimRows
          dimColumn
        """
        selectionRanges = self._getCurrentSelection()
        if len(selectionRanges)==1:
            model = self.model()
            topLeftIndex = selectionRanges[0].topLeft()
            bottomRightIndex = selectionRanges[0].bottomRight()
            # if top-left corner selection is inside data area
            if topLeftIndex.row() < model.rowDataCount():
                if topLeftIndex.column() < model.columnDataCount():
                    dimRows = bottomRightIndex.row() - topLeftIndex.row() + 1
                    dimColumns = bottomRightIndex.column() - topLeftIndex.column() + 1
                    return True, topLeftIndex, bottomRightIndex, dimRows, dimColumns
        return False, None, None, 0, 0

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

##############

    def _insertRows(self, insert=enums.InsertBlockDirectionEnum.BeforeInsert):
        isValid, topLeftIndex, bottomRightIndex, count, _ = self._getValidSelection()
        # it's a valid selection
        if isValid and count > 0:
                # insert rows
                row = topLeftIndex.row()
                if insert == enums.InsertBlockDirectionEnum.AfterInsert:
                    row = row + count
                model = self.model()
                model.insertRows(row, count)
                # new selection
                currentIndex = model.createIndex(row, topLeftIndex.column())
                self.setCurrentIndex(currentIndex)
                self.clearSelection()
                self._select(row,
                     topLeftIndex.column(),
                     row+count-1,
                     bottomRightIndex.column())

    def _insertEmptyArray(self, insert=enums.InsertDirectionEnum.TopInsert):
        isValid, topLeftIndex, bottomRightIndex, dimRows, dimColumns = self._getValidSelection()
        # it's a valid selection
        if isValid and dimRows > 0 and dimColumns > 0:
                # insert array
                row = topLeftIndex.row()
                column = topLeftIndex.column()
                model = self.model()
                if insert==enums.InsertDirectionEnum.TopInsert:
                    model.insertEmptyCellsInRows(row, column, dimRows, dimColumns)
                elif insert==enums.InsertDirectionEnum.BottomInsert:
                    row = row + dimRows
                    model.insertEmptyCellsInRows(row, column, dimRows, dimColumns)
                elif insert==enums.InsertDirectionEnum.LeftInsert:
                    model.insertEmptyCellsInColumns(row, column, dimRows, dimColumns)
                elif insert==enums.InsertDirectionEnum.RightInsert:
                    column = column + dimColumns
                    model.insertEmptyCellsInColumns(row, column, dimRows, dimColumns)
                # new selection
                currentIndex = model.createIndex(row, column)
                self.setCurrentIndex(currentIndex)
                self.clearSelection()
                self._select(row,
                             column,
                             row + dimRows - 1,
                             column + dimColumns - 1)

    def _removeArray(self, remove=enums.RemoveDirectionEnum.MoveLeftRemove):
        isValid, topLeftIndex, bottomRightIndex, dimRows, dimColumns = self._getValidSelection()
        # it's a valid selection
        if isValid and dimRows > 0 and dimColumns > 0:
                # remove array
                row = topLeftIndex.row()
                column = topLeftIndex.column()
                model = self.model()
                if remove==enums.RemoveDirectionEnum.MoveUpRemove:
                    model.removeArrayInRows(row, column, dimRows, dimColumns)
                if remove==enums.RemoveDirectionEnum.MoveLeftRemove:
                    model.removeArrayInColumns(row, column, dimRows, dimColumns)
                # new selection
                currentIndex = model.createIndex(row, column)
                self.setCurrentIndex(currentIndex)
                self.clearSelection()
                self._select(row,
                             column,
                             row + dimRows - 1,
                             column + dimColumns - 1)

    @helper.waiting
    def _moveArray(self, move):
        selection = self._getValidSelection2()
        if selection.isValid:
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            if dimRows > 0 and dimColumns > 0:
                startRow = selection.topLeftIndex.row()
                startColumn = selection.topLeftIndex.column()
                if move == enums.MoveDirectionEnum.LeftMove:
                    destRow = startRow
                    destColumn = startColumn - 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInColumns(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.RightMove:
                    destRow = startRow
                    destColumn = startColumn + 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInColumns(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.TopMove:
                    destRow = startRow - 1
                    destColumn = startColumn
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInRows(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                if move == enums.MoveDirectionEnum.BottomMove:
                    destRow = startRow + 1
                    destColumn = startColumn
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(destRow, destColumn, destRow + dimRows - 1, destColumn + dimColumns - 1)
                    self.document.moveArrayInRows(startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _mergeRows(self):
        selection = self._getValidSelection2()
        if selection.isValid:
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
        selection = self._getValidSelection2()
        if selection.isValid:
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
        selection = self._getValidSelection2()
        if selection.isValid:
            startRow = selection.topLeftIndex.row()
            startColumn = selection.topLeftIndex.column()
            dimRows = selection.dimRows
            dimColumns = selection.dimColumns
            # ok
            if dimRows > 0 and dimColumns > 0:
                if merge==enums.MergeDirectionEnum.MoveLeftRemove:
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow + dimRows -1, startColumn)
                    self.document.mergeArrayInColumns(startRow, startColumn, dimRows, dimColumns, None, undoSelection, redoSelection)
                else:
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(startRow, startColumn, startRow, startColumn + dimColumns - 1)
                    self.document.mergeArrayInRows(startRow, startColumn, dimRows, dimColumns, None, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _insertColumns(self, insert=enums.InsertBlockDirectionEnum.BeforeInsert):
        selection = self._getValidSelection2()
        if selection.isValid:
            count = selection.dimColumns
            if insert == enums.InsertBlockDirectionEnum.AfterInsert:
                column = selection.topLeftIndex.column() + count
            else:
                column = selection.topLeftIndex.column()
            # ok
            if count > 0:
                undoSelection = self._getCurrentSelection()
                redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                      column,
                                                      selection.bottomRightIndex.row(),
                                                      column + count - 1)
                self.document.insertEmptyColumns(column, count, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _removeRows(self):
        selection = self._getValidSelection2()
        if selection.isValid:
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
        selection = self._getValidSelection2()
        if selection.isValid:
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
        selection = self._getValidSelection2()
        if selection.isValid:
            count = selection.dimRows
            # ok
            if count > 0:
                if move == enums.MoveBlockDirectionEnum.BeforeMove:
                    startRow = selection.topLeftIndex.row()
                    destinationRow = startRow - 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row() - 1,
                                                          selection.topLeftIndex.column(),
                                                          selection.bottomRightIndex.row() - 1,
                                                          selection.bottomRightIndex.column())
                else:
                    startRow = selection.topLeftIndex.row()
                    destinationRow = startRow + 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row() + 1,
                                                          selection.topLeftIndex.column(),
                                                          selection.bottomRightIndex.row() + 1,
                                                          selection.bottomRightIndex.column())
                self.document.moveRows(startRow, count, destinationRow, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    @helper.waiting
    def _moveColumns(self, move=enums.MoveBlockDirectionEnum.AfterMove):
        selection = self._getValidSelection2()
        if selection.isValid:
            count = selection.dimColumns
            # ok
            if count > 0:
                if move == enums.MoveBlockDirectionEnum.BeforeMove:
                    startColumn = selection.topLeftIndex.column()
                    destinationColumn = startColumn - 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                          selection.topLeftIndex.column() - 1,
                                                          selection.bottomRightIndex.row(),
                                                          selection.bottomRightIndex.column() - 1)
                else:
                    startColumn = selection.topLeftIndex.column()
                    destinationColumn = startColumn + 1
                    undoSelection = self._getCurrentSelection()
                    redoSelection = self._getNewSelection(selection.topLeftIndex.row(),
                                                          selection.topLeftIndex.column() + 1,
                                                          selection.bottomRightIndex.row(),
                                                          selection.bottomRightIndex.column() + 1)
                self.document.moveColumns(startColumn, count, destinationColumn, undoSelection, redoSelection)
                self._setSelection(redoSelection)

    def _deleteCells(self, selectionRanges=None):
        # if no range, then get current selected range
        if selectionRanges == None:
            selectionModel = self.selectionModel()
            selectionRanges = selectionModel.selection()
        # delete cells
        model = self.model()
        for selectionRange in selectionRanges:
            topLeftIndex = selectionRange.topLeft()
            bottomRightIndex = selectionRange.bottomRight()
            row = topLeftIndex.row()
            column = topLeftIndex.column()
            dimRows = bottomRightIndex.row() - row + 1
            dimColumns = bottomRightIndex.column() - column + 1
            model.deleteCells(row, column, dimRows, dimColumns)

    def _selectedIndexesToRectangularArea(self, includeHeaderRows=False):
        """copy and convert selected indexes to string matrix"""
        result = None
        topLeftIndex = None
        bottomRightIndex = None
        selectedIndexes = self.selectedIndexes()
        if selectedIndexes:
            # get mix&max coordinates area from selected indexes
            topLeftIndex, bottomRightIndex = self._getMinMaxCoordinates(selectedIndexes)
            minColumn = topLeftIndex.column()
            minRow = topLeftIndex.row()
            maxColumn = bottomRightIndex.column()
            maxRow = bottomRightIndex.row()
            # get a two dimension matrix with default value ''
            result = []
            for _ in range(maxRow-minRow+1):
                row = [QString('') for _ in range(maxColumn-minColumn+1)]
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

    @helper.waiting
    def _rectangularAreaToSelectedIndex(self, array):
        selection = self._getValidSelection2()
        if selection.hasData:
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

    def _globalCut(self):
        selectionModel = self.selectionModel()
        QCsv._cuteSelectionRanges = selectionModel.selection()
        QCsv._cuteInstance = self

    @staticmethod
    def _globalPaste():
        clipboard = QApplication.clipboard()
        if clipboard.ownsClipboard():
            if hasattr(QCsv, '_cuteSelectionRanges') and hasattr(QCsv, '_cuteInstance'):
                if QCsv._cuteSelectionRanges:
                    QCsv._cuteInstance._deleteCells(QCsv._cuteSelectionRanges)
                    QCsv._cuteInstance.cancelClipboardAction.trigger()
                    QCsv._cuteSelectionRanges = None
                    QCsv._cuteInstance = None
        return

    def _editAction(self, action):
        textClip = None
        # copy to clipboard action
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
        # copy Column Name(s) action
        elif action == self.copyHeaderColumnsToClipboard:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toClipboard([matrix[0]])
        # copy As JSON action
        elif action == self.copyAsJSON:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toJSON(matrix)
        # copy As Delimited action
        elif action == self.copyAsDelimited:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toDelimitied(matrix)
        # copy As Delimited action
        elif action == self.copyAsXML:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toXML(matrix)
        # copy As Text action
        elif action == self.copyAsText:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toText(matrix)
        # copy As HTML action
        elif action == self.copyAsHTML:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toHTML(matrix)
        # copy Python Source Code As TEXT action
        elif action == self.copyPythonAsText:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonText(matrix)
        # copy Python Source Code As TUPLE action
        elif action == self.copyPythonAsTuple:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonTuple(matrix)
        # copy Python Source Code As LIST action
        elif action == self.copyPythonAsList:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonList(matrix)
        # copy Python Source Code As DICT action
        elif action == self.copyPythonAsDict:
            matrix = self._selectedIndexesToRectangularArea(includeHeaderRows=True)
            if matrix:
                textClip = lib.exports.ClipboardFormat.toPythonDict(matrix)

        #
        # at last copy result to clipboard
        #
        if textClip:
            clipboard = QApplication.clipboard()
            clipboard.setText(textClip, mode=QClipboard.Clipboard)
            return

        # paste from clipboard action
        if action == self.pasteFromClipboard:
            clipboard = QApplication.clipboard()
            textClip = clipboard.text()
            matrix = lib.imports.ClipboardFormat.toMatrix(textClip)
            self._rectangularAreaToSelectedIndex(matrix)
            self._globalPaste()
            return

        if action == self.insertColumnLeftAction:
            self._insertColumns(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            return

        if action == self.insertColumnRightAction:
            self._insertColumns(insert=enums.InsertBlockDirectionEnum.AfterInsert)
            return

        if action == self.insertRowTopAction:
            self._insertRows(insert=enums.InsertBlockDirectionEnum.BeforeInsert)
            return

        if action == self.insertRowBottomAction:
            self._insertRows(insert=enums.InsertBlockDirectionEnum.AfterInsert)
            return

        if action == self.removeRowsAction:
            self._removeRows()
            return

        if action == self.mergeRowsAction:
            self._mergeRows()
            return

        if action == self.removeColumnsAction:
            self._removeColumns()
            return

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

        if action == self.moveRowTopAction:
            self._moveRows(move=enums.MoveBlockDirectionEnum.BeforeMove)
            return

        if action == self.moveRowBottomAction:
            self._moveRows(move=enums.MoveBlockDirectionEnum.AfterMove)
            return

        if action == self.moveColumnLeftAction:
            self._moveColumns(move=enums.MoveBlockDirectionEnum.BeforeMove)
            return

        if action == self.moveColumnRightAction:
            self._moveColumns(move=enums.MoveBlockDirectionEnum.AfterMove)
            return

        if action == self.moveCellLeftAction:
            self._moveArray(move=enums.MoveDirectionEnum.LeftMove)
            return

        if action == self.moveCellRightAction:
            self._moveArray(move=enums.MoveDirectionEnum.RightMove)
            return

        if action == self.moveCellTopAction:
            self._moveArray(move=enums.MoveDirectionEnum.TopMove)
            return

        if action == self.moveCellBottomAction:
            self._moveArray(move=enums.MoveDirectionEnum.BottomMove)
            return

        if action ==  self.removeCellMoveUpAction:
            self._removeArray(remove=enums.RemoveDirectionEnum.MoveUpRemove)
            return

        if action == self.removeCellMoveLeftAction:
            self._removeArray(remove=enums.RemoveDirectionEnum.MoveLeftRemove)
            return

        if action == self.insertCellLeftAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.LeftInsert)
            return

        if action == self.insertCellRightAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.RightInsert)
            return

        if action == self.insertCellTopAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.TopInsert)
            return

        if action == self.insertCellBottomAction:
            self._insertEmptyArray(insert=enums.InsertDirectionEnum.BottomInsert)
            return

        if action == self.mergeCellsLeftAction:
            self._mergeArray(merge=enums.MergeDirectionEnum.MoveLeftRemove)
            return

        if action == self.mergeCellsTopAction:
            self._mergeArray(merge=enums.MergeDirectionEnum.MoveUpRemove)
            return

        if action == self.selectAllEdit:
            self.selectAll()
            return

        if action == self.deleteEdit:
            self._deleteCells()
            return

        if action == self.undoEdit:
            undoSelection = self.document.undo()
            self._setSelection(undoSelection)
            return

        if action == self.redoEdit:
            redoSelection = self.document.redo()
            self._setSelection(redoSelection)
            return

    def _addEditMenu(self):
        """add EDIT menu"""
        # edit menu
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
    # event
    #

    def _csvSelectionChangedEvent(self):
        """enable or disable menu options depending on the status"""
        numSelectedIndexes = len(self.selectedIndexes())
        self._setEditMenuDisabled(numSelectedIndexes == 0)

    def _csvcontextMenuRequestedEvent(self, selectedIndexes, globalPoint):
        """show popup edit menu"""
        self._editMenu.exec_(globalPoint)

    def _getMinMaxCoordinates(self, selectedIndexes):
        """get min and max coordinates from selected indexes"""
        minColumn = selectedIndexes[0].column()
        minRow = selectedIndexes[0].row()
        maxColumn = selectedIndexes[0].column()
        maxRow = selectedIndexes[0].row()
        for selectedIndex in selectedIndexes:
            if selectedIndex.column() < minColumn:
                minColumn = selectedIndex.column()
            if selectedIndex.row() < minRow:
                minRow = selectedIndex.row()
            if selectedIndex.column() > maxColumn:
                maxColumn = selectedIndex.column()
            if selectedIndex.row() > maxRow:
                maxRow = selectedIndex.row()
        model = self.model()
        topLeftIndex = model.createIndex(minRow, minColumn)
        bottomRightIndex = model.createIndex(maxRow, maxColumn)
        return topLeftIndex, bottomRightIndex

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

    def timerEvent(self, timerEvent):
        """override the method 'timerEvent' to give effect to the borders around
        the areas copied to clipboard"""
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

    def _redoTextChanged(self, msg, enable):
        self.redoEdit.setEnabled(enable)
        self.redoEdit.setText('Redo {}'.format(msg))

    def _undoTextChanged(self, msg, enable):
        self.undoEdit.setEnabled(enable)
        self.undoEdit.setText('Undo {}'.format(msg))

    #
    # public
    #

    selectionChanged_ = pyqtSignal()
    contextMenuRequested = pyqtSignal(list, QPoint)

    def encodingValue(self):
        return self.document.encoding

    def sizeValue(self):
        return helper.get_size(self.document.filename)

    def modifiedValue(self):
        modifiedDateTime = QDateTime(datetime.fromtimestamp(os.path.getmtime(self.document.filename)))
        strDateTime = modifiedDateTime.toString(Qt.SystemLocaleShortDate)
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

    def loadRequested(self):
        model = QCsvModel(self.document, config.config_headerrow)
        self.setModel(model)

    def setDocument(self, document):
        self.document = document
        self.document.loadRequested.connect(self.loadRequested)
        self.document.redoTextChanged.connect(self._redoTextChanged)
        self.document.undoTextChanged.connect(self._undoTextChanged)
        model = QCsvModel(self.document, config.config_headerrow)
        self.setModel(model)

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
        self.contextMenuRequested.connect(self._csvcontextMenuRequestedEvent)
        self.selectionChanged_.connect(self._csvSelectionChangedEvent)


##       self.setSortingEnabled(True)
##        # table model proxy
##       proxy = StringSortModel()
##        proxy.setSourceModel(self.tablemodel)
##
##        # tableview
##       self.setModel(self.tablemodel)#(proxy)

##        #prueba
##        actt = QAction(self)
##        actt.setShortcut('Ctrl+P')
##        actt.triggered.connect(self.actt)
##        self.addAction(actt)

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
