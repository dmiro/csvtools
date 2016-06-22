# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qcomboboxenter import QComboBoxEnter
from lib.enums import MatchModeEnum
from lib.config import config
from lib.helper import QStringToUnicode
import lib.images_rc
import sys

# para conseguir colorear texto, usar setItemDelegate
#http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt
#http://www.qtcentre.org/archive/index.php/t-22863.html


class QSearch(QWidget):

    #
    # public
    #

    searchClicked = pyqtSignal(str)
    resultClicked = pyqtSignal(str, int, int, str)

    def matchModeOption(self):
        index = self.matchMode.currentIndex()
        if index == 0:
            return MatchModeEnum.Contains
        if index == 1:
            return MatchModeEnum.WholeWord
        if index == 2:
            return MatchModeEnum.StartsWidth
        if index == 3:
            return MatchModeEnum.EndsWith
        if index == 4:
            return MatchModeEnum.RegularExpression

    def matchCaseOption(self):
        return self.matchCase.checkState() == Qt.Checked

    def findAllDocumentsOption(self):
        return self.findAllDocuments.checkState() == Qt.Checked

    def setResult(self, data):
        """ create and populate model with search result
            data struct is:
            [{'tabText':'tabText', 'tabToolTip': 'tabToolTip', 'result': [[row,col,value],..]},..]
        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Row',
                                         'Col',
                                         'Value'])
        self.result.setModel(model)
        self.result.setUniformRowHeights(True)
        self.toolBar.setDisabled(len(data) == 0)

        # iterate files
        for item in data:
            text = '{1} [{0}]'.format(len(item['result']), item['tabText'])
            parent = QStandardItem(text)
            parent.setEditable(False)
            parent.setToolTip(item['tabToolTip'])
            parent.setData(item['tabToolTip'], Qt.WhatsThisRole)
            # iterating over search result file
            for value in item['result']:
                row = QStandardItem(str(value[0]+1))
                row.setData(value, Qt.WhatsThisRole)
                row.setEditable(False)

                col = QStandardItem(str(value[1]+1))
                col.setData(value, Qt.WhatsThisRole)
                col.setEditable(False)

                text = QStandardItem(value[2])
                #text.setText('<font color=\"blue\">Hello</font> <font color=\"red\">World</font><font color=\"green">!</font>')
                text.setData(value, Qt.WhatsThisRole)
                text.setEditable(False)
                parent.appendRow([row, col, text])

            model.appendRow(parent)
            self.result.setFirstColumnSpanned(model.rowCount()-1, self.result.rootIndex(), True)

        self.result.expandAll()

    #
    # private
    #

    def _loadConfig(self):
        # text search
        self.textSearch.addItems(config.tools_searches)
        # match mode
        self.matchMode.setCurrentIndex(config.tools_matchMode)
        # match case
        if config.tools_matchCase:
            self.matchCase.setCheckState(Qt.Checked)
        # find all documents
        if config.tools_findAllDocuments:
            self.findAllDocuments.setCheckState(Qt.Checked)

    def _saveConfig(self):
        # text search
        config.tools_searches = [QStringToUnicode(self.textSearch.itemText(i)) for i in range(self.textSearch.count())]
        # match mode
        config.tools_matchMode = self.matchMode.currentIndex()
        # match case
        config.tools_matchCase = (self.matchCase.checkState() == Qt.Checked)
        # find all documents
        config.tools_findAllDocuments = (self.findAllDocuments.checkState() == Qt.Checked)

    def _textSearchAddText(self):
        """update list of recent searches"""
        text = self.textSearch.currentText()
        items = [self.textSearch.itemText(i) for i in range(self.textSearch.count())]
        if text in items:
            items.remove(text)
        items.insert(0, text)
        items = items[0:100]
        self.textSearch.clear()
        self.textSearch.addItems(items)
        self._saveConfig()

    def _getResultRow(self, item, row):
        return item.child(row, 0), item.child(row, 1), item.child(row, 2)

    def _firstResultItem(self):
        model = self.result.model()
        parent = model.index(0, 0)
        return self._getResultRow(parent, 0)

    def _lastResultItem(self):
        model = self.result.model()
        row = model.rowCount()
        parent = model.index(row-1, 0)
        row = model.rowCount(parent)
        return self._getResultRow(parent, row-1)

    def _nextResultItem(self):
        model = self.result.model()
        item = self.result.currentIndex()
        if item.isValid():
            parent = item.parent()
            # it's a valid item
            if parent.isValid():
                row = item.row()
                # item has a sibling
                if parent.child(row+1, 0).isValid():
                    return self._getResultRow(parent, row+1)
                # item hasn't a sibling
                else:
                    row = parent.row()
                    parent = model.index(row+1, 0)
                    if parent.isValid():
                        return self._getResultRow(parent, 0)
                    else:
                        return self._lastResultItem()
            # I'm in an item that has children
            else:
                return self._getResultRow(item, 0)
        return self._firstResultItem()

    def _prevResultItem(self):
        model = self.result.model()
        item = self.result.currentIndex()
        if item.isValid():
            parent = item.parent()
            # it's a valid item
            if parent.isValid():
                row = item.row()
                # item has a sibling
                if parent.child(row-1, 0).isValid():
                    return self._getResultRow(parent, row-1)
                # item hasn't a sibling
                else:
                    row = parent.row()
                    parent = model.index(row-1, 0)
                    if parent.isValid():
                        row = model.rowCount(parent)
                        return self._getResultRow(parent, row-1)
            # I'm in an item that has children
            else:
                return self._getResultRow(item, 0)
        # otherwise get firt item
        return self._firstResultItem()

    #
    # events
    #

    def _resultDoubleClickedEvent(self, index):
        """double click in result line event"""
        if index.isValid():
            parent = index.parent()
            if parent.isValid():
                file_ = parent.data(Qt.WhatsThisRole).toString()
                data = index.data(Qt.WhatsThisRole).toStringList()
                row = int(data[0])
                column = int(data[1])
                value = data[2]
                self.resultClicked.emit(file_, row, column, value)

    def _searchClickedEvent(self):
        """search button press event"""
        if self.search.isEnabled():
            self._textSearchAddText()
            text = self.textSearch.currentText()
            self.searchClicked.emit(text)

    def _textSearchEditTextChangedEvent(self, text):
        """edit text to find event"""
        if text:
            self.search.setEnabled(True)
        else:
            self.search.setEnabled(False)

    def _optionsChangedEvent(self):
        """changed search option event"""
        self._saveConfig()

    def _toolBarActionTriggeredEvent(self, action):
        if action == self.buttonFirst:
            child1, child2, child3 = self._firstResultItem()
        elif action == self.buttonPrev:
            child1, child2, child3 = self._prevResultItem()
        elif action == self.buttonNext:
            child1, child2, child3 = self._nextResultItem()
        else:
            child1, child2, child3 = self._lastResultItem()
        self.result.selectionModel().setCurrentIndex(child1, QItemSelectionModel.ClearAndSelect)
        self.result.selectionModel().setCurrentIndex(child2, QItemSelectionModel.Select)
        self.result.selectionModel().setCurrentIndex(child3, QItemSelectionModel.Select)
        self._resultDoubleClickedEvent(child1)

    #
    # init
    #

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        # textSearch widget
        self.textSearch = QComboBoxEnter()
        self.textSearch.setEditable(True)
        self.textSearch.setAutoCompletion(True)
        self.textSearch.setAutoCompletionCaseSensitivity(Qt.CaseSensitive)
        self.textSearch.setInsertPolicy(QComboBox.InsertAtTop)
        self.textSearch.setDuplicatesEnabled(False)
        self.textSearch.editTextChanged.connect(self._textSearchEditTextChangedEvent)
        self.textSearch.enter.connect(self._searchClickedEvent)

        # matchMode widget
        self.matchMode = QComboBox()
        self.matchMode.addItems(QStringList(['Contains',
                                             'Whole word',
                                             'Starts with',
                                             'Ends with',
                                             'Regular expression']))
        # matchCase widget
        self.matchCase = QCheckBox()

        # findAllDocuments widget
        self.findAllDocuments = QCheckBox()

        # button search widget
        self.search = QPushButton('Search')
        self.search.clicked.connect(self._searchClickedEvent)
        self._textSearchEditTextChangedEvent(str(self.textSearch.currentText()))

        # load config & connect changed event
        self._loadConfig()
        self.matchMode.currentIndexChanged.connect(self._optionsChangedEvent)
        self.matchCase.stateChanged.connect(self._optionsChangedEvent)
        self.findAllDocuments.stateChanged.connect(self._optionsChangedEvent)

        # navigate toolbar widget
        self.toolBar = QToolBar()
        ### self.buttonFirst = self.toolBar.addAction(QIcon(QPixmap(':images/first.png').scaled(12, 12, Qt.KeepAspectRatio)), '')
        self.buttonFirst = self.toolBar.addAction(QIcon(':images/first.png'), '')
        self.buttonPrev = self.toolBar.addAction(QIcon(':images/prev.png'), '')
        self.buttonNext = self.toolBar.addAction(QIcon(':images/next.png'), '')
        self.buttonLast = self.toolBar.addAction(QIcon(':images/last.png'), '')
        self.buttonFirst.setToolTip('first occurrence')
        self.buttonPrev.setToolTip('previous occurrence')
        self.buttonNext.setToolTip('next occurrence')
        self.buttonLast.setToolTip('last occurrence')
        self.toolBar.setIconSize(QSize(10, 10))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toolBar.setContentsMargins (0, 0, 0, 0)
        self.toolBar.actionTriggered.connect(self._toolBarActionTriggeredEvent)
        self.toolBar.setStyleSheet('.QToolBar{border:0px;}')
        self.toolBar.setDisabled(True)

        # grid widget
        self.grid = QFormLayout()
        self.grid.addRow(self.tr('Find what'), self.textSearch)
        self.grid.addRow(self.tr('Match mode'), self.matchMode)
        self.grid.addRow(self.tr('Match case'), self.matchCase)
        self.grid.addRow(self.tr('Find in all documents'), self.findAllDocuments)
        self.grid.addRow(self.search)

        # result tree view widget
        self.result= QTreeView()
        self.result.setAllColumnsShowFocus(True)
        self.result.doubleClicked.connect(self._resultDoubleClickedEvent)

        # main layout
        layout= QVBoxLayout()
        layout.addLayout(self.grid)
        layout.addWidget(self.result)
        layout.addWidget(self.toolBar, alignment=Qt.AlignRight)
        layout.setContentsMargins(4, 4, 4, 0)
        self.setLayout(layout)

