from PyQt4.QtCore import *
from PyQt4.QtGui import *
from helpers.qradiobuttongroup import QRadioButtonGroup
from helpers.qcheckboxgroup import QCheckGroupBox
from lib.document import Csv
from backports import csv
from lib.config import config

import lib.helper as helper
import sys


class TableModel(QAbstractTableModel):
    def __init__(self, document, parent=None, *args):
        super(TableModel, self).__init__(parent, *args)
        self.document = document

    def rowCount(self, parent=QModelIndex()):
        return self.document.rowCount()

    def columnCount(self, parent=QModelIndex()):
        return self.document.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            rowIndex = index.row()
            columnIndex = index.column()
            return self.document.value(rowIndex, columnIndex)

    def dataChangedEmit(self):
        topLeftIndex = self.createIndex(0, 0)
        bottomRightIndex = self.createIndex(self.rowCount(), self.columnCount())
        self.dataChanged.emit(topLeftIndex, bottomRightIndex)
        self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount() - 1)


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
            return unicode(self.buddie(6).text())

    def setValue(self, value):
        if value == u',':
            self.setChecked_(0, True)
        elif value == u';':
            self.setChecked_(1, True)
        elif value == u'\t':
            self.setChecked_(2, True)
        elif value == u'|':
            self.setChecked_(3, True)
        elif value == u':':
            self.setChecked_(4, True)
        elif value == u' ':
            self.setChecked_(5, True)
        else:
            self.setChecked_(6, True)
            self.buddie(6).setText(value)

    #
    # private
    #

    def __otherTextChangedSlot(self, text):
        self.selectItemChanged.emit(6, self.buddie(6))

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

    def setValue(self, value):
        if value == u'':
            self.setChecked_(0, True)
        elif value == u'"':
            self.setChecked_(1, True)
        elif value == u'\'':
            self.setChecked_(2, True)
        else:
            self.setChecked_(3, True)
            self.buddie(3).setText(value)

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
            return u'\r\n'
        if index == 1:
            return unicode(self.buddie(1).text())
        else:
            return u'\n'

    def setValue(self, value):
        if value == u'\r\n':
            self.setChecked_(0, True)
        elif value == u'\n':
            self.setChecked_(2, True)
        else:
            self.setChecked_(1, True)
            self.buddie(1).setText(value)

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

    def setSkipInitialSpace(self, value):
        self.setChecked_(0, value)

    def setDoubleQuote(self, value):
        self.setChecked_(1, value)

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

    def setValue(self, value):
        if value == csv.QUOTE_ALL:
            self.setChecked_(0, True)
        elif value == csv.QUOTE_MINIMAL:
            self.setChecked_(1, True)
        elif value == csv.QUOTE_NONNUMERIC:
            self.setChecked_(2, True)
        else:
            self.setChecked_(3, True)
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
    # private
    #

    @helper.waiting
    def __setValues(self):

        # change values
        if self.quoteGroupBox.value() == u'':
            self.quotingGroupBox.setValue(csv.QUOTE_NONE)

        # checking values
        checkingResult = []
        if self.delimiterGroupBox.value() == u'':
            checkingResult.append('* Delimiter needs value')
        if self.lineTerminatorGroupBox.value() == u'':
            checkingResult.append('* Line Terminator needs value')

        # disable widgets
        if len(checkingResult) > 0:
            self.labelMessage.setText('\n'.join(checkingResult))
            self.previewGroupBox.setEnabled(False)
            self.buttonBox.buttons()[0].setEnabled(False)

        # enable widgets
        else:
            self.labelMessage.setText('')
            self.previewGroupBox.setEnabled(True)
            self.buttonBox.buttons()[0].setEnabled(True)

            # set values
            self.__csv.delimiter = self.delimiterGroupBox.value()
            self.__csv.lineterminator = self.lineTerminatorGroupBox.value()
            self.__csv.quotechar = self.quoteGroupBox.value()
            self.__csv.skipinitialspace =  self.adjustsGroupBox.isSkipInitialSpace()
            self.__csv.doublequote = self.adjustsGroupBox.isDoubleQuote()
            self.__csv.quoting = self.quotingGroupBox.value()
            ##self.__csv.scapechar = u'@'

            # refresh preview
            if config.wizard_loadAllLines:
                if self.__inputIsChangeable:
                    self.__csv.load()
                text = self.__csv.toString()
                self.output.setText(text)
            else:
                if self.__inputIsChangeable:
                    self.__csv.load(config.wizard_linesToLoad)
                text = self.__csv.toString(config.wizard_linesToLoad)
                self.output.setText(text)
            model = self.preview.model()
            model.dataChangedEmit()

    #
    # slots
    #

    def __groupBoxClickedSlot(self):
        self.__setValues()

    #
    # widgets
    #

    def __addButtonBox(self):
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

    def __addPreviewGroupBox(self):

        # preview
        groupBoxPreview = QGroupBox(self.tr('Preview'), parent=self)
        layoutPreview = QHBoxLayout()
        groupBoxPreview.setLayout(layoutPreview)
        model = TableModel(self.__csv)
        self.preview = QTableView()
        self.preview.setModel(model)
        layoutPreview.addWidget(self.preview)

        # input
        if self.__inputIsChangeable:
            groupBoxInput = QGroupBox(self.tr('Input'), parent=self)
            layoutInput = QHBoxLayout()
            groupBoxInput.setLayout(layoutInput)
            self.input = QTextEdit()
            self.input.setReadOnly(True)
            layoutInput.addWidget(self.input)

        # output
        groupBoxOutput = QGroupBox(self.tr('Output'), parent=self)
        layoutOutput = QHBoxLayout()
        groupBoxOutput.setLayout(layoutOutput)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layoutOutput.addWidget(self.output)

        # splitters
        splitterSource = QSplitter(orientation= Qt.Horizontal)
        if self.__inputIsChangeable:
            splitterSource.addWidget(groupBoxInput)
        splitterSource.addWidget(groupBoxOutput)
        splitter = QSplitter(orientation= Qt.Vertical)
        splitter.addWidget(groupBoxPreview)
        splitter.addWidget(splitterSource)

        return splitter

    def __addCheckBoxWizard(self):
        checkBoxWizard = QCheckBox(self.tr('Show wizard next time'))
        checkBoxWizard.setStyleSheet("background-color: yellow; font: bold")
        checkBoxWizard.setCheckState(Qt.Checked)
        return checkBoxWizard

    def __addLabelMessage(self):
        labelMessage = QLabel('')
        labelMessage.setStyleSheet("color: red;")
        return labelMessage

    #
    # public
    #

    def document(self):
        return self.__csv

    def useWizard(self):
        return True if self.checkBoxWizard.checkState() == Qt.Checked else False

    #
    # init
    #

    def __init__(self, csv, inputIsChangeable=True, *args):
        QDialog.__init__ (self, *args)
        if not csv:
            raise IndexError('csv is mandatory')
        self.__csv = csv
        self.__inputIsChangeable = inputIsChangeable

        # widgets
        self.delimiterGroupBox = DelimiterGroupBox()
        self.quoteGroupBox = QuoteGroupBox()
        self.adjustsGroupBox = AdjustsGroupBox()
        self.lineTerminatorGroupBox = LineTerminatorGroupBox()
        self.quotingGroupBox = QuotingGroupBox()
        self.previewGroupBox = self.__addPreviewGroupBox()
        self.checkBoxWizard = self.__addCheckBoxWizard()
        self.buttonBox = self.__addButtonBox()
        self.labelMessage = self.__addLabelMessage()

        # set default values
        self.delimiterGroupBox.setValue(self.__csv.delimiter)
        self.quoteGroupBox.setValue(self.__csv.quotechar)
        self.lineTerminatorGroupBox.setValue(self.__csv.lineterminator)
        self.quotingGroupBox.setValue(self.__csv.quoting)
        self.adjustsGroupBox.setSkipInitialSpace(self.__csv.skipinitialspace)
        self.adjustsGroupBox.setDoubleQuote(self.__csv.doublequote)

        # signals
        self.delimiterGroupBox.selectItemChanged.connect(self.__groupBoxClickedSlot)
        self.quoteGroupBox.selectItemChanged.connect(self.__groupBoxClickedSlot)
        self.adjustsGroupBox.selectItemChanged.connect(self.__groupBoxClickedSlot)
        self.lineTerminatorGroupBox.selectItemChanged.connect(self.__groupBoxClickedSlot)
        self.quotingGroupBox.selectItemChanged.connect(self.__groupBoxClickedSlot)

        # layout
        grid = QGridLayout()
        grid.addWidget(self.delimiterGroupBox, 0, 0, 2, 1)
        grid.addWidget(self.quoteGroupBox, 0, 1, 2, 1)
        grid.addWidget(self.quotingGroupBox, 0, 3, 2, 1)
        grid.addWidget(self.adjustsGroupBox, 0, 2)
        grid.addWidget(self.lineTerminatorGroupBox, 1, 2)
        grid.addWidget(self.previewGroupBox, 2, 0, 1, 4)
        grid.addWidget(self.checkBoxWizard, 3, 3, 1, 1)
        grid.addWidget(self.buttonBox, 4, 0, 1, 4)
        grid.addWidget(self.labelMessage, 3, 0, 2, 1)

        # main
        self.setLayout(grid)
        self.setWindowTitle(self.tr('Csv Wizard'))

        # load input file only one time
        if self.__inputIsChangeable:
            if config.wizard_loadAllLines:
                text = self.__csv.fromString()
                self.input.setText(text)
            else:
                text = self.__csv.fromString(config.wizard_linesToLoad)
                self.input.setText(text)

        # set values
        self.__setValues()

        # set initial size
        self.resize(800, 600)


    #
    # class methods
    #

    @classmethod
    def getOpenFileName(cls, filename, parent = None):
        dialog = cls(Csv(filename))
        result = dialog.exec_()
        config.wizard_showToOpenFile = dialog.useWizard()
        if result == QDialog.Accepted:
            return dialog.document()
        else:
            return None

    @classmethod
    def getDropFileName(cls, filename, parent = None):
        dialog = cls(Csv(filename))
        result = dialog.exec_()
        config.wizard_showToDropFile = dialog.useWizard()
        if result == QDialog.Accepted:
            return dialog.document()
        else:
            return None

    @classmethod
    def getReloadFileName(cls, document, parent = None):
        docOrigin = document.shadowCopy()
        dialog = cls(document.shadowCopy())
        result = dialog.exec_()
        config.wizard_showToReloadFile = dialog.useWizard()
        if result == QDialog.Accepted:
            return dialog.document()
        else:
            document.setParameters(docOrigin)
            return None

    @classmethod
    def getSaveFileName(cls, document, parent = None):
        docOrigin = document.shadowCopy()
        dialog = cls(document, inputIsChangeable = False)
        result = dialog.exec_()
        config.wizard_showToSaveFile = dialog.useWizard()
        if result == QDialog.Accepted:
            return dialog.document()
        else:
            document.setParameters(docOrigin)
            return None

    @classmethod
    def getSaveNewFileName(cls, document, parent = None):
        docOrigin = document.shadowCopy()
        dialog = cls(document, inputIsChangeable = False)
        result = dialog.exec_()
        config.wizard_showSaveNewFile = dialog.useWizard()
        if result == QDialog.Accepted:
            return dialog.document()
        else:
            document.setParameters(docOrigin)
            return None





