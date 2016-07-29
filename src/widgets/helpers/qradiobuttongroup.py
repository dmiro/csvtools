from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QRadioButtonGroup(QGroupBox):

    #
    # public
    #

    selectItemChanged = pyqtSignal(int, QWidget)

    def selectedItem(self):
        return self.group.checkedId()

    def buddie(self, index):
        item = self.group.button(index)
        return item.buddie

    def setChecked_(self, index, isChecked):
        self.group.button(index).setChecked(isChecked)
        self.setEnabledBuddie()

    def addItem(self, text, widget=None, isChecked=False, toolTip=None):
        item = self.newItem(text, toolTip)
        index = len(self.group.buttons())
        self.group.addButton(item, index)
        item.buddie = widget
        if widget:
            row, column = self.__getRowCol(index)
            self.grid.addWidget(item, row, column)
            self.grid.addWidget(widget, row, column+1)
        else:
            row, column = self.__getRowCol(index)
            self.grid.addWidget(item, row, column)
        self.setChecked_(index, isChecked)
        return index

    def addItems(self, *items):
        for item in items:
            self.addItem(item)

    def removeItems(self):
        for item in self.group.buttons():
            self.group.removeButton(item)
            if item.buddie:
                self.grid.removeWidget(item.buddie)
                item.buddie = None
            self.grid.removeWidget(item)

    #
    # protected
    #

    def newItem(self, text, toolTip):
        item = QRadioButton(text)
        if toolTip:
            item.setToolTip(toolTip)
        return item

    def setEnabledBuddie(self):
        for item in self.group.buttons():
            if item.buddie:
                checked = item.isChecked()
                item.buddie.setEnabled(checked)

    #
    # private
    #

    def __getRowCol(self, index):
        row = index / self.columns + 1
        column = index % self.columns + 1
        column = column * 2 - 1
        return row, column

    def __groupClickedSlot(self, index):
        self.setEnabledBuddie()
        buddie = self.buddie(index)
        self.selectItemChanged.emit(index, buddie)

    #
    # init
    #

    def __init__(self, title='', columns=1):
        QGroupBox.__init__(self)
        self.setTitle(title)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.group = QButtonGroup()
        self.columns = columns
        QObject.connect(self.group, SIGNAL("buttonClicked(int)"),
                        self.__groupClickedSlot)


#
# test
#

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    main = QRadioButtonGroup(title='fiesta loca', columns=2)
    main.addItem('item 1', widget=QLineEdit())
    main.addItem('item 2', widget=QLineEdit())
    main.addItem('item 3')
    main.addItems('item 4', 'item 5')
    main.addItem('item 6', QLineEdit(), True)
    main.addItem('item 7', QLineEdit(), True)
    main.setChecked_(3,True)
    main.buddie(0).setText('text item 1')
    main.buddie(1).setText('text item 2')
    main.show()
    sys.exit(app.exec_())


