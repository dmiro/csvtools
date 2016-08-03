from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HLine(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__ (self, *args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class HLineLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__ (self, *args, **kwargs)
        self.setStyleSheet("color: white; background-color: black; padding-top: 2px; padding-bottom: 2px;")  # http://doc.qt.io/qt-4.8/stylesheet-reference.html

