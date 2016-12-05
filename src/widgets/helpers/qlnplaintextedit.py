from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QLNPlainTextEdit(QFrame):
    """
    Text widget with support for line numbers
    https://john.nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/
    """

    class NumberBar(QWidget):

        def __init__(self, edit):
            QWidget.__init__(self, edit)
            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.numberbarPaint(self, event)
            QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width(unicode(count)) + 10
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                # It would be nice to do
                # self.update(0, rect.y(), self.width(), rect.height())
                # But we can't because it will not remove the bold on the
                # current line if word wrap is enabled and a new block is
                # selected.
                self.update()


    class PlainTextEdit(QPlainTextEdit):

        def __init__(self, *args):
            QPlainTextEdit.__init__(self, *args)
            self.setFrameStyle(QFrame.NoFrame)
            self.highlight()
            #self.setLineWrapMode(QPlainTextEdit.NoWrap)
            self.cursorPositionChanged.connect(self.highlight)

        def highlight(self):
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(self.palette().alternateBase())
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])

        def numberbarPaint(self, number_bar, event):
            font_metrics = self.fontMetrics()
            current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

            block = self.firstVisibleBlock()
            line_count = block.blockNumber()
            painter = QPainter(number_bar)

            # paint background
            painter.fillRect(event.rect(), Qt.lightGray)
            painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

            # Iterate over all visible text blocks in the document.
            while block.isValid():
                line_count += 1
                block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

                # Check if the position of the block is out side of the visible area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break

                # We want the line number for the selected line to be bold.
                isCurrentLine = (line_count == current_line)
                font = painter.font()
                font.setBold(isCurrentLine)
                painter.setFont(font)

                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(0, block_top, number_bar.width() - 5, font_metrics.height())
                painter.drawText(paint_rect, Qt.AlignRight, unicode(line_count))
                block = block.next()

            painter.end()

    textChanged = pyqtSignal()

    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.edit = self.PlainTextEdit()
        self.number_bar = self.NumberBar(self.edit)

        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.edit.updateRequest.connect(self.number_bar.updateContents)
        self.edit.textChanged.connect(lambda: self.textChanged.emit())

    def toPlainText(self):
        return self.edit.toPlainText()

    def setPlainText(self, text):
        self.edit.setPlainText(text)

    def document(self):
        return self.edit.document()

    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)

    def lineWrapMode(self, mode):
        self.edit.lineWrapMode()

    def isModified(self):
        return self.edit.document().isModified()

    def setModified(self, modified):
        self.edit.document().setModified(modified)

    def textCursor(self):
        return self.edit.textCursor()
