from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qlnplaintextedit import QLNPlainTextEdit

import lib.images_rc
import lib.querycsv
import os


class Tables(QTreeWidget):

    def delData(self):
        self.clear()

    def setData(self, data):
        """
        :param data: [ ('table', ('field1', 'field2',...)), ...]
        :return: None
        """
        self.delData()
        for dataTable in data:
            table = QTreeWidgetItem(self)
            table.setText(0, dataTable[0])
            table.setIcon(0, QIcon(':images/table.png'))
            for dataField in dataTable[1]:
                field = QTreeWidgetItem(table)
                field.setText(0, dataField)
                field.setIcon(0, QIcon(':images/field.png'))

    #
    # init
    #

    def __init__(self, *args):
        QTreeWidget.__init__ (self, *args)
        self.setHeaderLabel('Tables')
        self.setIndentation(10)


class SQLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Sqlite SQL language.
       source:
       http://python.jpvweb.com/mesrecettespython/doku.php?id=pyqt4_colorisation_syntaxe_qtextedit
       https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    """

    # Keywords
    KEYWORDS = [
        'ABORT','COLUMN','ESCAPE','INSERT','ORDER','TABLE','ACTION','COMMIT',
        'EXCEPT','INSTEAD','OUTER','TEMP','ADD','CONFLICT','EXCLUSIVE',
        'INTERSECT','PLAN','TEMPORARY','AFTER','CONSTRAINT','EXISTS','INTO',
        'PRAGMA','THEN','ALL','CREATE','EXPLAIN','IS','PRIMARY','TO','ALTER',
        'CROSS','FAIL','ISNULL','QUERY','TRANSACTION','ANALYZE','CURRENT_DATE',
        'FOR','JOIN','RAISE','TRIGGER','AND','CURRENT_TIME','FOREIGN','KEY',
        'RECURSIVE','UNION','AS','CURRENT_TIMESTAMP','FROM','LEFT','REFERENCES',
        'UNIQUE','ASC','DATABASE','FULL','LIKE','REGEXP','UPDATE','ATTACH',
        'DEFAULT','GLOB','LIMIT','REINDEX','USING','AUTOINCREMENT','DEFERRABLE',
        'GROUP','MATCH','RELEASE','VACUUM','BEFORE','DEFERRED','HAVING','NATURAL',
        'RENAME','VALUES','BEGIN','DELETE','IF','NO','REPLACE','VIEW','BETWEEN',
        'DESC','IGNORE','NOT','RESTRICT','VIRTUAL','BY','DETACH','IMMEDIATE',
        'NOTNULL','RIGHT','WHEN','CASCADE','DISTINCT','IN','NULL','ROLLBACK',
        'WHERE','CASE','DROP','INDEX','OF','ROW','WITH','CAST','EACH','INDEXED',
        'OFFSET','SAVEPOINT','WITHOUT','CHECK','ELSE','INITIALLY','ON','SELECT',
        'COLLATE','END','INNER','OR','SET','TEXT','INTEGER','REAL','NUMERIC',
        'NONE','BLOB','TRUE','FALSE'
    ]

    def format(self, color, bold=None):
        """Return a QTextCharFormat with the given attributes.
        """
        textFormat = QTextCharFormat()
        textFormat.setForeground(color)
        if bold:
            textFormat.setFontWeight(QFont.Bold)
        return textFormat

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """

        # Do syntax formatting
        for expression, fmt in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do syntax formatting for comments multi-lines
        startIndex = 0
        if self.previousBlockState()!=1:
            startIndex = self.commentStartRegex.indexIn(text)

        while startIndex>=0:
            endIndex = self.commentEndRegex.indexIn(text, startIndex)
            if endIndex==-1:
                self.setCurrentBlockState(1)
                commentml_lg = len(text)-startIndex
            else:
                commentml_lg = endIndex-startIndex + self.commentEndRegex.matchedLength()
            self.setFormat(startIndex, commentml_lg, self.commentMultilineSyntaxStyle)
            startIndex = self.commentStartRegex.indexIn(text, startIndex + commentml_lg)

    #
    # init
    #

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Syntax styles
        keywordSyntaxStyle = self.format(Qt.blue)
        braceSyntaxStyle = self.format(Qt.black, bold=True)
        stringSyntaxStyle = self.format(Qt.magenta)
        commentSyntaxStyle = self.format(Qt.darkGreen)
        numbersSyntaxStyle = self.format(Qt.red)

        # Syntax style and QRegExp for comment multi-line pattern /*...*/
        self.commentMultilineSyntaxStyle = self.format(Qt.darkGreen)
        self.commentStartRegex = QRegExp("/\\*")
        self.commentEndRegex = QRegExp("\\*/")

        # Rules
        rules = [
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', stringSyntaxStyle),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", stringSyntaxStyle),
            # braces
            (r'[\)\(]+|[\{\}]+|[][]+', braceSyntaxStyle),
            # From '--' until a newline
            (r'--[^\n]*', commentSyntaxStyle),
            # Numeric literals
            ('\\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\\b', numbersSyntaxStyle)
        ]

        # Keyword rules
        rules += [(r'\b%s\b' % w, keywordSyntaxStyle)
            for w in SQLHighlighter.KEYWORDS]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(rule, Qt.CaseInsensitive), fmt)
            for (rule, fmt) in rules]


class Editor(QLNPlainTextEdit):

    isEmpty = pyqtSignal(bool)

    #
    # event
    #

    def __textChangedEvent(self):
        self.isEmpty.emit(self.isTextEmpty())

    #
    # public
    #

    def isTextEmpty(self):
        return not self.toPlainText()

    #
    # init
    #

    def __init__(self):
        QLNPlainTextEdit.__init__ (self)
        self.highlight = SQLHighlighter(self.document())
        self.textChanged.connect(self.__textChangedEvent)


class Result(QFrame):

    class TableModel(QAbstractTableModel):
        def __init__(self, parent=None, *args):
            QAbstractTableModel.__init__(self, *args)
            self.array_ = [[]]

        def rowCount(self, parent=QModelIndex()):
            return len(self.array_)

        def columnCount(self, parent=QModelIndex()):
            return len(self.array_[0])

        def data(self, index, role):
            if not index.isValid():
                return QVariant()
            if role == Qt.DisplayRole or role == Qt.EditRole:
                rowIndex = index.row()
                columnIndex = index.column()
                return self.array_[rowIndex][columnIndex]

        def setArray(self, array_):
            self.array_ = array_

    #
    # public
    #

    def setResult(self, result):
        if isinstance(result, list):
            print 'list'
            self.modelResult.setArray(result)
            self.box.setCurrentWidget(self.tableResult)
        else:
            print 'string'
            self.textResult.setPlainText(result)
            self.box.setCurrentWidget(self.textResult)

    #
    # init
    #

    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        self.textResult = QPlainTextEdit()
        self.textResult.setReadOnly(True)

        self.modelResult = self.TableModel()
        self.tableResult = QTableView()
        self.tableResult.setModel(self.modelResult)

        self.box = QStackedLayout(self)
        self.box.addWidget(self.textResult)
        self.box.addWidget(self.tableResult)
        self.box.setCurrentWidget(self.textResult)


class Tab(QTabWidget):

    isEmpty = pyqtSignal(bool)

    #
    # private
    #

    def __getScriptForFilename(self, filename):
        for index in xrange(self.count()):
            tabFilename = self.tabToolTip(index)
            if tabFilename == filename:
                return index
        return None

    #
    # event
    #

    def __isEmptyEvent(self, empty):
        self.isEmpty.emit(empty)

    def __currentChangedEvent(self, index):
        editor = self.widget(index)
        if editor:
            empty = editor.isTextEmpty()
            self.isEmpty.emit(empty)

    def __tabCloseRequestedEvent(self, index):
        self.removeTab(index)

    #
    # public
    #

    def addScript(self, filename, script=''):
        index = self.__getScriptForFilename(filename)
        # if filename doesn't exist create tab
        if index == None:
            editor = Editor()
            editor.setPlainText(script)
            index = self.addTab(editor, os.path.basename(filename))
            self.setTabToolTip(index, filename)
            editor.isEmpty.connect(self.__isEmptyEvent)
        self.setCurrentIndex(index)

    def newScript(self):
        filename = 'script {0}'.format(self.countNewScript)
        self.countNewScript = self.countNewScript + 1
        self.addScript(filename)


    #
    # init
    #

    def __init__(self):
        QTabWidget.__init__ (self)
        self.countNewScript = 1
        self.setTabsClosable(True)
        self.setMovable(True)
        self.currentChanged.connect(self.__currentChangedEvent)
        self.tabCloseRequested.connect(self.__tabCloseRequestedEvent)


class ToolBar(QToolBar):

    #
    # public
    #

    runQueryRequested = pyqtSignal()
    newQueryRequested = pyqtSignal()
    loadQueryRequested = pyqtSignal()

    showColumnWizardRequested = pyqtSignal()

    #
    # event
    #

    def __menuOptionClickedEvent(self):
        heightWidget = self.optionsButton.height()
        point = self.optionsButton.mapToGlobal(QPoint(0, heightWidget))
        self.optionsMenu.exec_(point)

    def __toolBarActionTriggeredEvent(self, action):

        # options button
        if action == self.showResultInTab:
            pass
        elif action == self.showResultBelow:
            pass
        elif action == self.showResultToNewCsv:
            pass
        elif action == self.showColumnWizard:
            self.showColumnWizardRequested.emit()
            pass

        # actions
        elif action == self.runQueryAction:
            self.runQueryRequested.emit()
        elif action == self.newQueryAction:
            self.newQueryRequested.emit()
        elif action == self.loadQueryAction:
            self.loadQueryRequested.emit()
        elif action == self.saveQueryAction:
            pass

    #
    # init
    #

    def __init__(self):
        QToolBar.__init__ (self)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # actions
        self.runQueryAction = QAction(QIcon(':images/play.png'), self.tr('Run script (F5)'), self)
        self.runQueryAction.setShortcut('F5')
        self.newQueryAction = QAction(QIcon(':images/new.png'), self.tr('New script'), self)
        self.loadQueryAction = QAction(QIcon(':images/open.png'), self.tr('Open script'), self)
        self.saveQueryAction = QAction(QIcon(':images/save.png'), self.tr('Save script'), self)
        self.showResultInTab = QAction(self.tr('Result in tab'), self)
        self.showResultInTab.setCheckable(True)
        self.showResultInTab.setChecked(True)
        self.showResultBelow = QAction(self.tr('Result below'), self)
        self.showResultBelow.setCheckable(True)
        self.showResultToNewCsv = QAction(self.tr('Result to new csv'), self)
        self.showResultToNewCsv.setCheckable(True)
        self.showColumnWizard = QAction('Show column wizard', self)
        self.showColumnWizard.setCheckable(True)
        self.showColumnWizard.setChecked(True)

        # options button
        self.optionsMenu = QMenu()
        self.optionsMenu.addAction(self.showResultInTab)
        self.optionsMenu.addAction(self.showResultBelow)
        self.optionsMenu.addAction(self.showResultToNewCsv)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction(self.showColumnWizard)
        self.optionsMenu.triggered.connect(self.__toolBarActionTriggeredEvent)
        #
        actionGroup = QActionGroup(self.optionsMenu)
        self.showResultInTab.setActionGroup(actionGroup)
        self.showResultBelow.setActionGroup(actionGroup)
        self.showResultToNewCsv.setActionGroup(actionGroup)
        #
        self.optionsButton = QToolButton()
        self.optionsButton.setMenu(self.optionsMenu)
        self.optionsButton.setIcon(QIcon(':images/filteroptions.png'))
        self.optionsButton.setStatusTip(self.tr('Options'))
        self.optionsButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.optionsButton.clicked.connect(self.__menuOptionClickedEvent)

        # toolbar
        self.setIconSize(QSize(16, 16))
        self.addAction(self.runQueryAction)
        self.addAction(self.newQueryAction)
        self.addAction(self.loadQueryAction)
        self.addAction(self.saveQueryAction)
        self.addSeparator()
        self.addWidget(self.optionsButton)
        self.actionTriggered.connect(self.__toolBarActionTriggeredEvent)


class QQueryCsv(QDialog):

    #
    # private
    #

    def __setTables(self):
        """
        Get list of tables and fields in the database
        """
        data = []
        tables = lib.querycsv.query_sqlite('SELECT tbl_name FROM sqlite_master WHERE type="table"', self.db)
        tables = [table[0] for table in tables[1:]]
        for tableName in tables:
            tableInfo = lib.querycsv.query_sqlite('PRAGMA table_info(''{0}'')'.format(tableName), self.db)
            tableInfo = (tableName, [field[1] for field in tableInfo[1:]])
            data.append(tableInfo)
        self.tables.setData(data)

    #
    # event
    #

    def __runQueryRequested(self):

        currentScript = self.tab.currentWidget()
        if currentScript:
            script = currentScript.toPlainText()
            script = unicode(script)

        # test   u'select * from result where name="dog"'
        _array = [
        [u'name', u'number', u'color'],
        [u'cat', u'1', u'red'],
        [u'dog', u'2', u'green'],
        [u'bird', u'3', u'blue']
        ]
        lib.querycsv.import_array(self.db, _array, 'result', overwrite=True)
        lib.querycsv.import_array(self.db, _array, 'result2', overwrite=True)
        lib.querycsv.import_array(self.db, _array, 'result3', overwrite=True)
        #
        self.__setTables()
        #
        try:
            results = lib.querycsv.query_sqlite(script, self.db)
            print results
            self.result.setResult(results)
        except Exception as ex:
            print 'me', ex.message
            self.result.setResult(ex.message)
        # test
        self.runQueryRequested.emit()

    def __newQueryRequested(self):
        self.tab.newScript()

    def __loadQueryRequested(self):
        filename = QFileDialog.getOpenFileName(parent = self, caption = self.tr('Open'), filter = 'All Files (*.*);;Scripts (*.sql *.qry)')
        if filename:
            filename = str(filename)
            with open(filename, 'r') as fileScript:
                script = fileScript.read()
                self.tab.addScript(filename, script)

    def __showColumnWizardRequested(self):
        isVisible = not self.tables.isVisible()
        self.tables.setVisible(isVisible)

    def __isEmptyEvent(self, empty):
        self.toolbar.runQueryAction.setDisabled(empty)

    #
    # widgets
    #

    ##def __addButtonBox(self):
    ##    pass

    #
    # public
    #

    runQueryRequested = pyqtSignal()

    def importCsv(self, csv):
        #':memory:'
        #lib.querycsv.import_array(array, table_name, header=None, overwrite=False):
        #lib.querycsv.import_array(self.db, self.array, 'result')
        #results = query_sqlite('select * from result where name="dog"', self.db)
        pass

    #
    # init
    #

    def __init__(self, *args):
        QDialog.__init__ (self, *args)

        import sqlite3
        self.db = sqlite3.connect(':memory:')

        # widgets
        self.toolbar = ToolBar()
        self.tab = Tab()
        self.result = Result()

        # events
        self.toolbar.runQueryRequested.connect(self.__runQueryRequested)
        self.toolbar.newQueryRequested.connect(self.__newQueryRequested)
        self.toolbar.loadQueryRequested.connect(self.__loadQueryRequested)
        self.toolbar.showColumnWizardRequested.connect(self.__showColumnWizardRequested)

        # tab
        self.tab.isEmpty.connect(self.__isEmptyEvent)
        self.tab.newScript()
        self.tables = Tables()

        # splitter
        self.editSplitter = QSplitter(Qt.Vertical)
        self.editSplitter.addWidget(self.tab)
        self.editSplitter.addWidget(self.result)
        self.editSplitter.setStretchFactor(0, 5)
        self.editSplitter.setStretchFactor(1, 1)

        # splitter
        self.mainSplitter= QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.tables)
        self.mainSplitter.addWidget(self.editSplitter)
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 5)

        # main layout
        layout= QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.mainSplitter)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)
        self.setWindowTitle(self.tr('Query Csv'))
