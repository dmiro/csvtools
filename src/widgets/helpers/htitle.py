from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HTitle(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__ (self, *args, **kwargs)
        # http://doc.qt.io/qt-4.8/stylesheet-reference.html
        self.setStyleSheet("""
        color: white;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 black, stop: 0.8 gray, stop:1 white);
        margin-top: 3px;
        padding-left: 1px;
        padding-top: 2px;
        padding-bottom: 2px;
        """)

