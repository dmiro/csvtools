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
        self.sheet = super(CommandSheet, sheet)
        self.row = row
        self.column = column
        self.cellValue = cellValue

    def redo(self):
        self.value = self.sheet.value(self.row, self.column)
        self.sheet.setValue(self.row, self.column, self.cellValue)

    def undo(self):
        self.sheet.setValue(self.row, self.column, self.value)


class CommandInsertEmptyColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, count, undoSelection, redoSelection):
        description = 'insert {} empty columns at [:,{}]'.format(count, startColumn)
        super(CommandInsertEmptyColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
        self.startRow = startRow
        self.rows = rows
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(self.startRow, 0, self.rows, self.sheet.columnCount())
        self.sheet.mergeRows(self.startRow, self.rows, self.separator)

    def undo(self):
        self.sheet.removeRows(self.startRow, 1)
        self.sheet.insertRows(self.startRow, self.redoArray)


class CommandMergeColumns(QUndoSelectionCommand):

    def __init__(self, sheet, startColumn, columns, separator, undoSelection, redoSelection):
        description = 'merge {} columns at [:,{}]'.format(columns, startColumn)
        super(CommandMergeColumns, self).__init__(description, undoSelection, redoSelection)
        self.sheet = super(CommandSheet, sheet)
        self.startColumn = startColumn
        self.columns = columns
        self.separator = separator

    def redo(self):
        self.redoArray = self.sheet.getArray(0, self.startColumn, self.sheet.rowCount(), self.columns)
        self.sheet.mergeColumns(self.startColumn, self.columns, self.separator)

    def undo(self):
        self.sheet.removeColumns(self.startColumn, 1)
        self.sheet.insertColumns(self.startColumn, self.redoArray)

class CommandMergeArrayInRows(QUndoSelectionCommand):

    def __init__(self, sheet, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        description = 'merge array {}x{} in rows at [{},{}]'.format(dimRows, dimColumn, startRow, startColumn)
        super(CommandMergeArrayInRows, self).__init__(description, undoSelection, redoSelection)
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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
        self.sheet = super(CommandSheet, sheet)
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


class CommandSheet(QObject, Sheet):

    redoTextChanged = pyqtSignal(str, bool)
    undoTextChanged = pyqtSignal(str, bool)

    #
    # init
    #

    def __init__(self, valueClass, arrayData=None):
        QObject.__init__(self)                          # In a multiple inheritance it's hard to use 'super(CommandSheet, self).__init__(valueClass, arrayData)'
        Sheet.__init__(self, valueClass, arrayData)     # http://www.gossamer-threads.com/lists/python/python/445708
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

    def setValue(self, row, column, cellValue):
        command = CommandSetValue(self, row, column, cellValue, None, None)
        self.stack.push(command)

    def insertEmptyColumns(self, startColumn, count, undoSelection, redoSelection):
        command = CommandInsertEmptyColumns(self, startColumn, count, undoSelection, redoSelection)
        self.stack.push(command)

    def removeRows(self, startRow, count, undoSelection, redoSelection):
        command = CommandRemoveRows(self, startRow, count, undoSelection, redoSelection)
        self.stack.push(command)

    def removeColumns(self, startColumn, count, undoSelection, redoSelection):
        command = CommandRemoveColumns(self, startColumn, count, undoSelection, redoSelection)
        self.stack.push(command)

    def moveRows(self, startRow, count, destinationRow, undoSelection, redoSelection):
        command = CommandMoveRows(self, startRow, count, destinationRow, undoSelection, redoSelection)
        self.stack.push(command)

    def moveColumns(self, startColumn, count, destinationColumn, undoSelection, redoSelection):
        command = CommandMoveColumns(self, startColumn, count, destinationColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeRows(self, startRow, rows, separator, undoSelection, redoSelection):
        command = CommandMergeRows(self, startRow, rows, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeColumns(self, startColumn, columns, separator, undoSelection, redoSelection):
        command = CommandMergeColumns(self, startColumn, columns, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeArrayInRows(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        command = CommandMergeArrayInRows(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def mergeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection):
        command = CommandMergeArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, separator, undoSelection, redoSelection)
        self.stack.push(command)

    def moveArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        command = CommandMoveArrayInColumns(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def moveArrayInRows(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection):
        command = CommandMoveArrayInRows(self, startRow, startColumn, dimRows, dimColumns, destRow, destColumn, undoSelection, redoSelection)
        self.stack.push(command)

    def setArrayRepeater(self, startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection):
        command = CommandSetArrayRepeater(self, startRow, startColumn, dimRows, dimColumns, array, undoSelection, redoSelection)
        self.stack.push(command)

