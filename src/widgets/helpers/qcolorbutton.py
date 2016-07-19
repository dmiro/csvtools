from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QColorButton(QPushButton):
    """
    Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()
        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        """
        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))
        if dlg.exec_():
            self.setColor(dlg.currentColor().name())
        """
        if self._color:
            color = QColorDialog.getColor(QColor(self._color))
        else:
            color = QColorDialog.getColor(Qt.white)
        if color.isValid():
            self.setColor(color.name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)
        return super(QColorButton, self).mousePressEvent(e)


    """
    from PyQt4 import QtCore, QtGui

class ColorBox(QtGui.QFrame):

    def __init__(self,parent=None):
        super(ColorBox,self).__init__(parent)

        self.bgColor = QtCore.Qt.white
        self.setFixedHeight(20)
        self.setFrameStyle(1)
        self.setStyleSheet("QWidget { border-color: rgba(0,0,0,0)}")

    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton:
            col = QtGui.QColorDialog.getColor(self.bgColor, self)

            if col.isValid():
                rgb = (col.red(), col.green(), col.blue())
                self.setStyleSheet("QWidget { background-color: rgb(%d,%d,%d) }" % rgb)
                self.bgColor = col


if __name__ == "__main__":
    app = QtGui.QApplication([])
    c = ColorBox()
    c.show()
app.exec_()
    """