from PyQt4.QtCore import *
from PyQt4.QtGui import *
from helpers.qradiobuttongroup import QRadioButtonGroup
from helpers.qcheckboxgroup import QCheckGroupBox
from widgets.csvm import QCsv
from lib.document import Csv
from backports import csv

import sys


class DelimiterGroupBox(QRadioButtonGroup):

    #
    # public
    #

    def value(self):
        index = self.selectedItem()
        if index == 0:
            return u','
        elif index == 1:
            return u';'
        elif index == 2:
            return u'\t'
        elif index == 3:
            return u'|'
        elif index == 4:
            return u':'
        elif index == 5:
            return u' '
        else:
            return unicode(self.buddie(4).text())

    #
    # private
    #

    def __otherTextChangedSlot(self, text):
        self.selectItemChanged.emit(4, self.buddie(4))

    #
    # init
    #

    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Delimiter', columns=2)
        self.addItem(self.tr('Comma (,)'))
        self.addItem(self.tr('Semicolon (;)'))
        self.addItem(self.tr('Tab'))
        self.addItem(self.tr('Vertical bar (|)'))
        self.addItem(self.tr('Colon (:)'))
        self.addItem(self.tr('Space'))
        other = QLineEdit()
        other.textChanged.connect(self.__otherTextChangedSlot)
        other.setMaxLength(1)
        self.addItem(self.tr('Other'), widget=other)


class QuoteGroupBox(QRadioButtonGroup):

    #
    # public
    #

    def value(self):
        index = self.selectedItem()
        if index == 0:
            return u''
        elif index == 1:
            return u'"'
        elif index == 2:
            return u'\''
        else:
            return unicode(self.buddie(3).text())

    #
    # private
    #

    def __otherTextChangedSlot(self, text):
        self.selectItemChanged.emit(3, self.buddie(3))

    #
    # init
    #

    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Quote Char', columns=1)
        self.addItem(self.tr('None'))
        self.addItem(self.tr('Double quote (")'))
        self.addItem(self.tr('Quote (\')'))
        other = QLineEdit()
        other.textChanged.connect(self.__otherTextChangedSlot)
        other.setMaxLength(1)
        self.addItem(self.tr('Other'), widget=other)


class LineTerminatorGroupBox(QRadioButtonGroup):

    #
    # public
    #

    def value(self):
        index = self.selectedItem()
        if index == 0:
            return u'\\r\\n'
        if index == 1:
            return unicode(self.buddie(1).text())
        else:
            return u'\\n'

    #
    # private
    #

    def __otherTextChangedSlot(self, text):
        self.selectItemChanged.emit(1, self.buddie(1))

    #
    # init
    #

    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Line Terminator', columns=2)
        self.addItem(self.tr('\\r\\n'))
        other = QLineEdit()
        other.textChanged.connect(self.__otherTextChangedSlot)
        self.addItem(self.tr('Other'), widget=other)
        self.addItem(self.tr('\\n'))


class AdjustsGroupBox(QCheckGroupBox):

    #
    # public
    #

    def isSkipInitialSpace(self):
        return 0 in self.selectedItems()

    def isDoubleQuote(self):
        return 1 in self.selectedItems()

    #
    # init
    #

    def __init__(self):
        QCheckGroupBox.__init__ (self, title='Adjusts', columns=2)
        self.addItem(self.tr('Skip initial space'))
        self.addItem(self.tr('Double quote'))


class QuotingGroupBox(QRadioButtonGroup):

    #
    # public
    #

    def value(self):
        index = self.selectedItem()
        if index == 0:
            return csv.QUOTE_ALL
        if index == 1:
            return csv.QUOTE_MINIMAL
        if index == 2:
            return csv.QUOTE_NONNUMERIC
        if index == 3:
            return csv.QUOTE_NONE

    #
    # init
    #

    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Quoting', columns=1)
        self.setToolTip('Controls when quotes should be generated by the [writer] and recognised by the [reader]')
        self.addItem(self.tr('All'), toolTip=self.tr('[writer] Quote all fields'))
        self.addItem(self.tr('Minimal'), toolTip=self.tr('[writer] Only quote fields which contain special characters such as delimiter, quotechar or any of the characters in lineterminator'))
        # Instructs the reader to convert all non-quoted fields to type float.
        self.addItem(self.tr('Non numeric'), toolTip=self.tr('[writer] Quote all non-numeric fields\n[reader] Convert all non-quoted fields to type float'))
        # Instructs writer objects to never quote fields. When the current delimiter occurs in output data it is preceded by the current
        # escapechar character. If escapechar is not set, the writer will raise Error if any characters that require escaping are encountered.
        # Instructs reader to perform no special processing of quote characters.
        self.addItem(self.tr('None'), toolTip=self.tr('[writer] Never quote fields\n[reader] Perform no special processing of quote characters'))

class QCsvWiz(QDialog):

    #
    # widgets
    #

    def _addButtonBox(self):
        acceptButton = QPushButton(self.tr('Accept'), self)
        acceptButton.setIcon(QIcon(':images/accept.png'))
        cancelButton = QPushButton(self.tr('Cancel'), self)
        cancelButton.setIcon(QIcon(':images/cancel.png'))
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(lambda: self.accept())
        buttonBox.rejected.connect(lambda: self.reject())
        return buttonBox

    def _addPreviewGroupBox2(self):
        groupBox = QGroupBox(self.tr('Preview'), parent=self)
        formLayout = QFormLayout(parent=groupBox)
        # Preview TableView
        csvDocument = Csv(self.filename)
        csvDocument.load(20)
        self.preview = QCsv(csvDocument)
##        self.preview.setEnabled(False)
        formLayout.addRow(self.preview)
        return groupBox

    def _addSourceGroupBox(self):
        groupBox = QGroupBox(self.tr('Source'), parent=self)
        formLayout = QFormLayout(parent=groupBox)
        self.input = QTextEdit()
        self.output = QTextEdit()
        splitter = QSplitter(orientation= Qt.Horizontal)
        splitter.addWidget(self.input)
        splitter.addWidget(self.output)
        formLayout.addRow(splitter)
        return groupBox

    def _addPreviewGroupBox(self):

        groupBox1 = QGroupBox(self.tr('Preview'), parent=self)
        layout1 = QFormLayout(parent=groupBox1)
        csvDocument = Csv(self.filename)
        csvDocument.load(20)
        self.preview = QCsv(csvDocument)
        layout1.addRow(self.preview)

        groupBox2 = QGroupBox(self.tr('Input'), parent=self)
        layout2 = QFormLayout(parent=groupBox2)
        self.input = QTextEdit()
        layout2.addRow(self.input)

        groupBox3 = QGroupBox(self.tr('Output'), parent=self)
        layout3 = QFormLayout(parent=groupBox3)
        self.output = QTextEdit()
        layout3.addRow(self.output)


        splitter1 = QSplitter(orientation= Qt.Horizontal)
        splitter1.addWidget(groupBox2)
        splitter1.addWidget(groupBox3)

    #    w4 = QWidget()
    #    w4.setLayout(splitter1)

        splitter2 = QSplitter(orientation= Qt.Vertical)
        splitter2.addWidget(groupBox1)
        splitter2.addWidget(splitter1)

    #    w5 = QWidget()
    #    w5.setLayout(splitter2)

        return splitter2

    #
    # slots
    #

    def _groupBoxClickedSlot(self):
        print 'delimiterGroupBox', self.delimiterGroupBox.value()
        print 'lineTerminatorGroupBox', self.lineTerminatorGroupBox.value()
        print 'quoteGroupBox', self.quoteGroupBox.value()
        #csvDocument = Csv(self.filename,
        #                       delimiter =self.delimiterGroupBox.value())
        #csvDocument.load()
        #self.preview.setDocument(csvDocument)
##        print 'skipinitialspace', self.preview.document.skipinitialspace

        self.preview.document.delimiter = self.delimiterGroupBox.value()
        self.preview.document.lineterminator = self.lineTerminatorGroupBox.value()
        self.preview.document.quotechar = self.quoteGroupBox.value()
        self.preview.document.skipinitialspace =  self.adjustsGroupBox.isSkipInitialSpace()
        self.preview.document.doublequote = self.adjustsGroupBox.isDoubleQuote()
        self.preview.document.quoting = self.quotingGroupBox.value()
        self.preview.document.scapechar = u'@'

     #   self.preview.document.quoting = True

        self.preview.document.load(20)

        ##self.preview.data = data

       # self.preview.setEnabled(False)


    #
    # init
    #

    def __init__(self, filename, *args):
        QDialog.__init__ (self, *args)
        self.filename = filename

        # widgets
        self.buttonBox = self._addButtonBox()
        self.delimiterGroupBox = DelimiterGroupBox()
        self.quoteGroupBox = QuoteGroupBox()
        self.adjustsGroupBox = AdjustsGroupBox()
        self.lineTerminatorGroupBox = LineTerminatorGroupBox()
        self.quotingGroupBox = QuotingGroupBox()
        self.previewGroupBox = self._addPreviewGroupBox()

        # signals
        self.delimiterGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.quoteGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.adjustsGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.lineTerminatorGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.quotingGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)

        # layout
        grid = QGridLayout()
        grid.addWidget(self.delimiterGroupBox, 0, 0, 2, 1)
        grid.addWidget(self.quoteGroupBox, 0, 1, 2, 1)
        grid.addWidget(self.quotingGroupBox, 0, 3, 2, 1)#
        grid.addWidget(self.adjustsGroupBox, 0, 2)
        grid.addWidget(self.lineTerminatorGroupBox, 1, 2)
        grid.addWidget(self.previewGroupBox, 2, 0, 1, 4)
        grid.addWidget(self.buttonBox, 3, 0, 1, 4)

        # main
        self.setLayout(grid)
        self.setWindowTitle(self.tr('Import Csv'))
        ##self.setFixedSize(800, 400)

