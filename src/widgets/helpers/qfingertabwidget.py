from PyQt4.QtCore import *
from PyQt4.QtGui import *


class QFingerTabWidget(QTabBar):

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        painter.begin(self)
        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, Qt.AlignVCenter | Qt.TextDontClip, self.tabText(index))
        painter.end()

    def tabSizeHint(self,index):
        return self.tabSize

    #
    # init
    #

    def __init__(self, *args, **kwargs):
        self.tabSize = QSize(kwargs.pop('width'), kwargs.pop('height'))
        super(QFingerTabWidget, self).__init__(*args, **kwargs)


#
# test
#

if __name__ == '__main__':

    # https://gist.github.com/LegoStormtroopr/5075267
    import sys
    app = QApplication(sys.argv)
    tabs = QTabWidget()
    tabs.setTabBar(QFingerTabWidget(width=100, height=25))
    digits = ['Thumb', 'Pointer', 'Rude', 'Ring', 'Pinky']
    for i,d in enumerate(digits):
        widget =  QLabel("Area #%s <br> %s Finger"% (i,d))
        tabs.addTab(widget, d)
    tabs.setTabPosition(QTabWidget.West)
    tabs.show()
    sys.exit(app.exec_())