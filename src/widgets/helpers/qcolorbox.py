from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QColorBox(QFrame):
    """
    Custom Qt Widget to show a choosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to default color.
    """

    colorChanged = pyqtSignal()

    def __init__(self, parent=None, defaultColor=Qt.white):
        super(QColorBox,self).__init__(parent)

        self.setStyleSheet("border-color: rgba(0,0,0,0);")
        self.__color = None
        self.__defaultColor = QColor(defaultColor)
        self.setColor(self.__defaultColor)
        self.setFixedHeight(20)
        self.setFrameStyle(1)

    def setColor(self, color):
        if color != self.__color:
            self.__color = QColor(color)
            self.setStyleSheet("background-color: %s;" % self.__color.name())
            self.colorChanged.emit()

    def color(self):
        return self.__color

    def mousePressEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            color = QColorDialog.getColor(self.__color)
            if color.isValid():
                self.setColor(color)
                self.colorChanged.emit()
        elif e.button() == Qt.RightButton:
            self.setColor(self.__defaultColor)

#
# test
#

if __name__ == "__main__":
    app = QApplication([])
    c = QColorBox()
    c.show()
    c.setColor(Qt.red)
    app.exec_()
