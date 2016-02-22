from PyQt4.QtCore import *
from PyQt4.QtGui import *

class QElidedLabel(QLabel):
    _width = _text = _elided = None

    def __init__(self, text='', width=40, parent=None):
        super(QElidedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)

    def elidedText(self):
        return self._elided or ''

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, Qt.ElideRight, width)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawItemText(
            painter, rect, self.alignment(), option.palette,
            self.isEnabled(), self._elided, self.foregroundRole())
