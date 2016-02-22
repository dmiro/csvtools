from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HLine(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__ (self, *args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


