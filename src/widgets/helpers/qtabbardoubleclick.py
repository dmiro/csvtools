from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QTabBarDoubleClick(QTabBar):

    doubleClick = pyqtSignal(int)

    def __init__ (self, *args):
        super(QTabBarDoubleClick, self).__init__(*args)

    def mouseDoubleClickEvent(self, event):
        super(QTabBarDoubleClick, self).mouseDoubleClickEvent(event)
        self.doubleClick.emit(self.currentIndex())
