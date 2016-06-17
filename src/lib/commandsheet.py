from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.enums as enums
import lib.undostack as undostack
from lib.sheet import Sheet

class QUndoSelectionCommand(QUndoCommand):

    def __init__(self, description, undoSelection, redoSelection):
        super(QUndoSelectionCommand, self).__init__(description)
        self.undoSelection = undoSelection
        self.redoSelection = redoSelection


class CommandSetValue(QUndoSelectionCommand):

    def __init__(self, sheet, row, column, cellValue, undoSelection, redoSelection):
        description = 'set value at [{},{}]'.format(row, column)
        super(CommandSetValue, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.row = row
        self.column = column
        self.cellValue = cellValue

    def redo(self):
        self.value = self.sheet.value(self.row, self.column)
        self.sheet.setValue(self.row, self.column, self.cellValue)

    def undo(self):
        self.sheet.setValue(self.row, self.column, self.value)

class CommandInsertEmptyRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, count, undoSelection, redoSelection):
        description = 'insert {} empty rows at [{},:]'.format(count, startRow)
        super(CommandInsertEmptyRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.count = count

    def redo(self):
        self.sheet.insertEmptyRows(self.startRow, self.count)

    def undo(self):
        self.sheet.removeRows(self.startRow, self.count)

class CommandInsertEmptyColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, count, undoSelection, redoSelection):
        description = 'insert {} empty columns at [:,{}]'.format(count, startColumn)
        super(CommandInsertEmptyColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startColumn = startColumn
        self.count = count

    def redo(self):
        self.sheet.insertEmptyColumns(self.startColumn, self.count)

    def undo(self):
        self.sheet.removeColumns(self.startColumn, self.count)


class CommandRemoveRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, count, undoSelection, redoSelection):
        description = 'remove {} rows at [{},:]'.format(count, startRow)
        super(CommandRemoveRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.count = count

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow,  0, self.count, self.sheet.columnCount())
        self.sheet.removeRows(self.startRow, self.count)

    def undo(self):
        self.sheet.insertRows(self.startRow, self.redoArray)


class CommandRemoveColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, count, undoSelection, redoSelection):
        description = 'remove {} columns at [:,{}]'.format(count, startColumn)
        super(CommandRemoveColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startColumn = startColumn
        self.count = count

    def redo(self):
        self.redoArray = self.sheet.getArray(0, self.startColumn, self.sheet.rowCount(), self.count)
        self.sheet.removeColumns(self.startColumn, self.count)

    def undo(self):
        self.sheet.insertColumns(self.startColumn, self.redoArray)


class CommandMoveRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, count, destinationRow, undoSelection, redoSelection):
        description = 'move {} rows from [{},:] to [{},:]'.format(count, startRow, destinationRow)
        super(CommandMoveRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.count = count
        self.destinationRow = destinationRow

    def redo(self):
        self.sheet.moveRows(self.startRow, self.count, self.destinationRow)

    def undo(self):
        self.sheet.moveRows(self.destinationRow, self.count, self.startRow)


class CommandMoveColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, count, destinationColumn, undoSelection, redoSelection):
        description = 'move {} columns from [:,{}] to [:,{}]'.format(count, startColumn, destinationColumn)
        super(CommandMoveColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startColumn = startColumn
        self.count = count
        self.destinationColumn = destinationColumn

    def redo(self):
        self.sheet.moveColumns(self.startColumn, self.count, self.destinationColumn)

    def undo(self):
        self.sheet.moveColumns(self.destinationColumn, self.count, self.startColumn)


class CommandMergeRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, rows, separator, undoSelection, redoSelection):
        description = 'merge {} rows at [{},:]'.format(rows, startRow)
        super(CommandMergeRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.rows = rows
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, 0, self.rows, self.sheet.columnCount())
        #self.sheet.mergeRows(self.startRow, self.rows, self.separator)
        self.sheet.mergeArrayInRows(self.startRow,
                                    0,
                                    self.rows,
                                    self.sheet.columnCount(),
                                    self.separator)

    def undo(self):
        self.sheet.removeRows(self.startRow, 1)
        self.sheet.insertRows(self.startRow, self.redoArray)


class CommandMergeColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, columns, separator, undoSelection, redoSelection):
        description = 'merge {} columns at [:,{}]'.format(columns, startColumn)
        super(CommandMergeColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startColumn = startColumn
        self.columns = columns
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(0, self.startColumn, self.sheet.rowCount(), self.columns)
        #self.sheet.mergeColumns(self.startColumn, self.columns, self.separator)
        self.sheet.mergeArrayInColumns(0,
                                       self.startColumn,
                                       self.sheet.rowCount(),
                                       self.columns,
                                       self.separator)

    def undo(self):
        self.sheet.removeColumns(self.startColumn, 1)
        self.sheet.insertColumns(self.startColumn, self.redoArray)

class CommandMergeArrayInRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        description = 'merge array {}x{} in rows at [{},{}]'.format(dimRows, dimColumn, startRow, startColumn)
        super(CommandMergeArrayInRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, self.startColumn, self.dimRows, self.dimColumns)
        self.sheet.mergeArrayInRows(self.startRow, self.startColumn, self.dimRows, self.dimColumns, self.separator)

    def undo(self):
        self.sheet.removeArrayInRows(self.startRow, self.startColumn, 1, self.dimColumns)
        self.sheet.insertArrayInRows(self.startRow, self.startColumn, self.redoArray)

class CommandMergeArrayInColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        description = 'merge array {}x{} in columns at [{},{}]'.format(dimRows, dimColumns, startRow, startColumn)
        super(CommandMergeArrayInColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, self.startColumn, self.dimRows, self.dimColumns)
        self.sheet.mergeArrayInColumns(self.startRow, self.startColumn, self.dimRows, self.dimColumns, self.separator)

    def undo(self):
        self.sheet.removeArrayInColumns(self.startRow, self.startColumn, self.dimRows, 1)
        self.sheet.insertArrayInColumns(self.startRow, self.startColumn, self.redoArray)


class CommandMoveArrayInColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        description = 'move array {}x{} from [{},{}] to [{},{}]'.format(dimRows, dimColumns, startRow, startColumn, destRow, destColumn)
        super(CommandMoveArrayInColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns
        self.destRow = destRow
        self.destColumn = destColumn

    def redo(self):
        self.sheet.moveArrayInColumns(self.startRow, self.startColumn, self.dimRows, self.dimColumns, self.destRow, self.destColumn)

    def undo(self):
        self.sheet.moveArrayInColumns(self.destRow, self.destColumn, self.dimRows, self.dimColumns, self.startRow, self.startColumn)


class CommandMoveArrayInRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        description = 'move array {}x{} from [{},{}] to [{},{}]'.format(dimRows, dimColumns, startRow, startColumn, destRow, destColumn)
        super(CommandMoveArrayInRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns
        self.destRow = destRow
        self.destColumn = destColumn

    def redo(self):
        self.sheet.moveArrayInRows(self.startRow, self.startColumn, self.dimRows, self.dimColumns, self.destRow, self.destColumn)

    def undo(self):
        self.sheet.moveArrayInRows(self.destRow, self.destColumn, self.dimRows, self.dimColumns, self.startRow, self.startColumn)


class CommandSetArrayRepeater(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection):
        description = 'set array {}x{} to [{},{}]'.format(dimRows, dimColumns, startRow, startColumn)
        super(CommandSetArrayRepeater, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns
        self.array = array
        # get row and column dimensions array to redo operation
        self.dimArrayRows = dimRows
        self.dimArrayColumns = dimColumns
        if array != None:
            dim = len(array)
            if dimRows < dim:
                self.dimArrayRows = dim
            if dim:
                dim = max(len(row) for row in array)
                if dimColumns < dim:
                    self.dimArrayColumns = dim

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, self.startColumn, self.dimArrayRows, self.dimArrayColumns)
        self.sheet.setArrayRepeater(self.startRow, self.startColumn, self.dimRows, self.dimColumns, self.array)

    def undo(self):
        self.sheet.setArray(self.startRow, self.startColumn, self.redoArray)


class CommandRemoveArrayInColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection):
        description = 'remove array {}x{} at [{},{}]'.format(dimRows, dimColumns, startRow, startColumn)
        super(CommandRemoveArrayInColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, self.startColumn, self.dimRows, self.dimColumns)
        self.sheet.removeArrayInColumns(self.startRow, self.startColumn, self.dimRows, self.dimColumns)

    def undo(self):
        self.sheet.insertArrayInColumns(self.startRow, self.startColumn, self.redoArray)


class CommandRemoveArrayInRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection):
        description = 'remove array {}x{} at [{},{}]'.format(dimRows, dimColumns, startRow, startColumn)
        super(CommandRemoveArrayInRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = sheet
        self.startRow = startRow
        self.startColumn = startColumn
        self.dimRows = dimRows
        self.dimColumns = dimColumns

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, self.startColumn, self.dimRows, self.dimColumns)
        self.sheet.removeArrayInRows(self.startRow, self.startColumn, self.dimRows, self.dimColumns)

    def undo(self):
        self.sheet.insertArrayInRows(self.startRow, self.startColumn, self.redoArray)


class CommandSheet(QObject):

    redoTextChanged = pyqtSignal(str, bool)
    undoTextChanged = pyqtSignal(str, bool)

    #
    # init
    #

    def __init__(self, valueClass, arrayData=None):
        QObject.__init__(self)
        self.sheet = Sheet(valueClass, arrayData)
        self.stack = QUndoStack()
        undostack.globalUndoStack.addStack(self.stack)
        self.stack.redoTextChanged.connect(lambda msg: self.redoTextChanged.emit(msg, self.stack.canRedo()))
        self.stack.undoTextChanged.connect(lambda msg: self.undoTextChanged.emit(msg, self.stack.canUndo()))

    #
    # del
    #

    def __del__(self):
        try:
            self.stack.setClean()
            globalUndoStack.removeStack(self.stack)
        except:
            pass

    #
    # public
    #

    def arrayData(self):
        return self.sheet.arrayData()

    def setArrayData(self, arrayData):
        self.sheet.setArrayData(arrayData)

    def rowCount(self):
        return self.sheet.rowCount()

    def columnCount(self):
        return self.sheet.columnCount()

    def isEmpty(self):
        return self.sheet.isEmpty()

    def value(self, row, column):
        return self.sheet.value(row, column)

    def search(self, text, matchMode, matchCaseOption):
        return self.sheet.search(text, matchMode, matchCaseOption)

    def getArray(self, startRow, startColumn, dimRows, dimColumns, transpose=False):
        return self.sheet.getArray(startRow, startColumn, dimRows, dimColumns, transpose)

    #
    # public undo and redo methods
    #

    def undo(self):
        index = self.stack.index()
        if index > 0:
            index = index-1
            command = self.stack.command(index)
            if command:
                data = command.undoSelection
                self.stack.undo()
                return data
        return None

    def redo(self):
        index = self.stack.index()
        if index < self.stack.count():
            command = self.stack.command(index)
            if command:
                data = command.redoSelection
                self.stack.redo()
                return data
        return None

    #
    # public undo command methods
    #

    def setValue(self, row, column, cellValue):
        command = CommandSetValue(self.sheet, row, column, cellValue, None, None)
        self.stack.push(command)

    def removeColumns(self, startColumn, count, undoSelection, redoSelection):
        command = CommandRemoveColumns(self.sheet, startColumn, count, undoSelection, redoSelection)
        self.stack.push(command)

    def removeColumn(self, startColumn, undoSelection, redoSelection):
        self.removeColumns(startColumn, 1, undoSelection, redoSelection)

    def removeRows(self, startRow, count, undoSelection, redoSelection):
        command = CommandRemoveRows(self.sheet, startRow, count, undoSelection, redoSelection)
        self.stack.push(command)

    def removeRow(self, startRow, undoSelection, redoSelection):
        self.removeRows(startRow, 1, undoSelection, redoSelection)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertRows(self, startRow, rows):
        self.sheet.insertRows(startRow, rows)

    def insertEmptyRows(self, startRow, count, undoSelection, redoSelection):
        command = CommandInsertEmptyRows(self.sheet, startRow, count, undoSelection, redoSelection)
        self.stack.push(command)

    def insertEmptyRow(self, startRow, undoSelection, redoSelection):
        self.insertEmptyRows(startRow, 1, undoSelection, redoSelection)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertColumns(self, startColumn, columns):
        self.sheet.insertColumns(startColumn, columns)

    def insertEmptyColumns(self, startColumn, count, undoSelection, redoSelection):
        command = CommandInsertEmptyColumns(self.sheet, startColumn, count, undoSelection, redoSelection)
        self.stack.push(command)

    def insertEmptyColumn(self, startColumn, undoSelection, redoSelection):
        self.insertEmptyColumns(startColumn, 1, undoSelection, redoSelection)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertArrayInColumns(self, startRow, startColumn, array):
        self.sheet.insertArrayInColumns(startRow, startColumn, array)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertEmptyCellsInColumns(self, startRow, startColumn, dimRows, dimColumns):
        self.sheet.insertEmptyCellsInColumns(startRow, startColumn, dimRows, dimColumns)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertArrayInRows(self, startRow, startColumn, array):
        self.sheet.insertArrayInRows(startRow, startColumn, array)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def insertEmptyCellsInRows(self, startRow, startColumn, dimRows, dimColumns):
        self.sheet.insertEmptyCellsInRows(startRow, startColumn, dimRows, dimColumns)

    def removeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection):
        command = CommandRemoveArrayInColumns(self.sheet, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
        self.stack.push(command)

    def removeArrayInRows(self, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection):
        command = CommandRemoveArrayInRows(self.sheet, startRow, startColumn, dimRows, dimColumns, undoSelection, redoSelection)
        self.stack.push(command)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def deleteCells(self, startRow, startColumn, dimRows, dimColumns):
        self.sheet.deleteCells(startRow, startColumn, dimRows, dimColumns)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # este no ---> def setArray(self, startRow, startColumn, array):
    def setArrayRepeater(self, startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection):
        command = CommandSetArrayRepeater(self.sheet, startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeArrayInRows(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        command = CommandMergeArrayInRows(self.sheet, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        command = CommandMergeArrayInColumns(self.sheet, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def moveRows(self, startRow, count, destinationRow, undoSelection, redoSelection):
        command = CommandMoveRows(self.sheet, startRow, count, destinationRow, undoSelection, redoSelection)
        self.stack.push(command)

    def moveRow(self, startRow, destinationRow, undoSelection, redoSelection):
        self.moveRows(startRow, 1, destinationRow, undoSelection, redoSelection)

    def moveColumns(self, startColumn, count, destinationColumn, undoSelection, redoSelection):
        command = CommandMoveColumns(self.sheet, startColumn, count, destinationColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def moveColumn(self, startColumn, destinationColumn, undoSelection, redoSelection):
        self.moveColumns(startColumn, 1, destinationColumn, undoSelection, redoSelection)

    def moveArrayInRows(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        command = CommandMoveArrayInRows(self.sheet, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeRows(self, startRow, rows, separator, undoSelection, redoSelection):
        command = CommandMergeRows(self.sheet, startRow, rows, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def moveArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        command = CommandMoveArrayInColumns(self.sheet, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeColumns(self, startColumn, columns, separator, undoSelection, redoSelection):
        command = CommandMergeColumns(self.sheet, startColumn, columns, separator, undoSelection, redoSelection)
        self.stack.push(command)






















