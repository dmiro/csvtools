from PyQt4.QtCore import *
from PyQt4.QtGui import *

class VLine(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__ (self, *args, **kwargs)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

