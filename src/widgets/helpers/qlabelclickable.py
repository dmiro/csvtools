from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QLabelClickable(QLabel):

    clicked = pyqtSignal()

    def __init__(self, *args):
        QLabel.__init__(self, *args)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()

