from PyQt4.QtGui import *
from PyQt4.QtCore import *

 
class QComboBoxEnter(QComboBox):

    enter = pyqtSignal()
    
    def __init__(self, *args):
        QComboBox.__init__(self, *args)
   
    def keyPressEvent(self, e):
        QComboBox.keyPressEvent(self, e)
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.enter.emit()
