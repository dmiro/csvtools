from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qradiobuttongroup import QRadioButtonGroup


class QCheckGroupBox(QRadioButtonGroup):

    #
    # public
    #
    
    def selectedItems(self):
        result = [] 
        for item in self.group.buttons():
            if item.checkState() == Qt.Checked:
                index = self.group.id(item) 
                result.append(index)
        return result

    def setChecked_(self, index, isChecked):        
        item = self.group.button(index)
        if isChecked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)
        self.setEnabledBuddie()

    #
    # protected
    #
    
    def newItem(self, text):
        return QCheckBox(text)
    
    def setEnabledBuddie(self):
        for item in self.group.buttons():
            if item.buddie:
                checked = item.checkState() == Qt.Checked
                item.buddie.setEnabled(checked)

    #
    # init
    #
    
    def __init__(self, title='', columns=1):
        QRadioButtonGroup.__init__(self, title, columns)
        self.group.setExclusive(False)

#
# test
#

if __name__ == '__main__':
    
    import sys
    app = QApplication(sys.argv)
    main = QCheckGroupBox(title='fiesta loca', columns=2)
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
            
