from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.enums as enums
import lib.undostack as undostack
from lib.sheet import Sheet


class CommandSetValue(QUndoCommand):

    def __init__(self, sheet, row, column, cellValue):
        description = 'set value at %d %d' % (row, column)
        super(CommandSetValue, self).__init__(description)
        self.sheet = super(CommandSheet, sheet)
        self.row = row
        self.column = column
        self.cellValue = cellValue

    def redo(self):
        self.value = self.sheet.value(self.row, self.column)
        self.sheet.setValue(self.row, self.column, self.cellValue)

    def undo(self):
        self.sheet.setValue(self.row, self.column, self.value)


class CommandRemoveColumns(QUndoCommand):

    def __init__(self, sheet, startColumn, count):
        description = 'remove %d columns at %d column' % (count, startColumn)
        super(CommandRemoveColumns, self).__init__(description)
        self.sheet = super(CommandSheet, sheet)
        self.startColumn = startColumn
        self.count = count

    def redo(self):
        self.array = self.sheet.getArray(0, self.startColumn, self.sheet.rowCount(), self.count)
        self.sheet.removeColumns(self.startColumn, self.count)

    def undo(self):
        self.sheet.insertColumns(self.startColumn, self.array)


class CommandSheet(Sheet):

 #   undoRedoRequested = pyqtSignal(object)

    #
    # init
    #

    def __init__(self, valueClass, arrayData=None):
        super(CommandSheet, self).__init__(valueClass, arrayData)
        self.stack = QUndoStack()
        undostack.globalUndoStack.addStack(self.stack)

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
        print 'undo', index
        if index > 0:
            index = index-1
            command = self.stack.command(index)
            print 'command', command.text()
            if command:
                data = 'hello' #command.data
                self.stack.undo()
          #      self.undoRedoRequested.emit(data)
                return data
        return None

    def redo(self):
        index = self.stack.index()
        print 'redo', index
        if index < self.stack.count():
            command = self.stack.command(index)
            print 'command', command.text()
            if command:
                data = 'hello' #command.data
                self.stack.redo()
          #      self.undoRedoRequested.emit(data)
                return data
        return None

    def setValue(self, row, column, cellValue):
        command = CommandSetValue(self, row, column, cellValue)
        self.stack.push(command)

    def removeColumns(self, startColumn, count):
        command = CommandRemoveColumns(self, startColumn, count)
        self.stack.push(command)

