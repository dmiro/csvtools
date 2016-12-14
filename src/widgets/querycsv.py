from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qlnplaintextedit import QLNPlainTextEdit
from lib.helper import waiting, QStringMatrixToUnicode

import lib.images_rc
import lib.querycsv
import lib.helper

import os


class Tables(QTreeWidget):

    #
    # private
    #

    def __extractTableName(self, item):
        text = item.text(0)
        text = unicode(text)
        return text[:text.rfind('(') - 1]

    #
    # public
    #

    def delData(self):
        self.clear()

    def setData(self, data):
        """
        :param data: [ ('table', 250, ('field1', 'field2',...)), ...]
        :return: None
        """
        self.delData()
        for dataTable in data:
            table = QTreeWidgetItem(self)
            table.setText(0, '{0} ({1})'.format(dataTable[0], dataTable[1]))
            table.setIcon(0, QIcon(':images/table.png'))
            for dataField in dataTable[2]:
                field = QTreeWidgetItem(table)
                field.setText(0, dataField)
                field.setIcon(0, QIcon(':images/field.png'))

    #
    # event
    #

    def __customContextMenuRequestedEvent(self, position):
        """show popup edit menu"""

        #itemIndex = self.itemAt(position)
        #if itemIndex:
        #    if not itemIndex.parent():
        #        self.setCurrentItem(itemIndex)

        # crear un menu en funcion de los items seleccionados:
        # - SELECT *
        # - SELECT <all fields>
        # - SELECT <selected fields>
        # - SELECT * ... WHERE <selected fields>
        # - SELECT <selected fields> ... WHERE <selected fields>

        # - SELECT * ... JOIN <selected tables>
        # - SELECT * ... JOIN <selected tables> WHERE <selected fields>
        # - SELECT <all fields> ... JOIN <selected tables>
        # - SELECT <selected fields> ... JOIN <selected tables>

        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

            menu = QMenu()
            if level == 0:
                menu.addAction(self.tr("Edit Table"))
            elif level == 1:
                menu.addAction(self.tr("Edit Field"))

            menu.exec_(self.viewport().mapToGlobal(position))

    def __itemDoubleClickedEvent (self, item, column):
        if item:
            script = ""
            if item.childCount() > 0:
                script = 'select * from "{0}"'.format(self.__extractTableName(item))
            else:
                script = '"{0}"."{1}"'.format(self.__extractTableName(item.parent()), item.text(0))
            print script

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

        script = []
        selectedItems = self.selectedItems()
        for item in selectedItems:
            if item.childCount() > 0:
                script.append('"{0}"'.format(self.__extractTableName(item)))
            else:
                script.append('"{0}"."{1}"'.format(self.__extractTableName(item.parent()), item.text(0)))
        script = ','.join(script)

        mimeData = QMimeData()
        mimeData.setText(script)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(Qt.CopyAction)

    #
    # init
    #

    def __init__(self, *args):
        QTreeWidget.__init__ (self, *args)
        self.setHeaderLabel('Tables')
        self.setIndentation(10)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemDoubleClicked.connect(self.__itemDoubleClickedEvent)
        self.setAcceptDrops(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__customContextMenuRequestedEvent)


class SQLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Sqlite SQL language.
       source:
       http://python.jpvweb.com/mesrecettespython/doku.php?id=pyqt4_colorisation_syntaxe_qtextedit
       https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    """

    # Sqlite Keywords
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
            # Numeric literals
            ('\\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\\b', numbersSyntaxStyle),
            # From '--' until a newline (this rule is mandatory in the last position)
            (r'--[^\n]*', commentSyntaxStyle)
        ]

        # Keyword rules
        rules = [(r'\b%s\b' % w, keywordSyntaxStyle)
                 for w in SQLHighlighter.KEYWORDS] + rules

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
    # override
    #

    def toPlainText(self):
        cursor = self.textCursor()
        textSelected = cursor.selectedText()
        if textSelected:
            return unicode(textSelected)
        else:
            return unicode(QLNPlainTextEdit.toPlainText(self))

    #
    # init
    #

    def __init__(self):
        QLNPlainTextEdit.__init__ (self)
        self.highlight = SQLHighlighter(self.document())
        self.textChanged.connect(self.__textChangedEvent)
        self.setAcceptDrops(True)


class Result(QFrame):

    class TableModel(QAbstractTableModel):
        def __init__(self, array_):
            QAbstractTableModel.__init__(self)
            self.array_ = array_

        def rowCount(self, parent=QModelIndex()):
            return len(self.array_) - 1

        def columnCount(self, parent=QModelIndex()):
            return len(self.array_[0])

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                value = self.array_[0][section]
                return value
            return QAbstractTableModel.headerData(self, section, orientation, role)

        def data(self, index, role):
            if not index.isValid():
                return QVariant()
            if role == Qt.DisplayRole or role == Qt.EditRole:
                rowIndex = index.row() + 1
                columnIndex = index.column()
                return self.array_[rowIndex][columnIndex]

    class TableResult(QTableView):

        def __getCurrentSelection(self):
            selectionModel = self.selectionModel()
            return selectionModel.selection()

        def __getHeaderValue(self, column):
            model = self.model()
            value = model.headerData(column, orientation=Qt.Horizontal, role = Qt.DisplayRole)
            return value

        def __getValue(self, row, column):
            model = self.model()
            index = model.createIndex (row, column)
            value = model.data(index, role = Qt.DisplayRole)
            return value

        def __copy(self, includeHeaders, includeRowNumbers):
            selectedRanges = self.__getCurrentSelection()
            if len(selectedRanges) == 1:
                topLeftIndex = selectedRanges[0].topLeft()
                bottomRightIndex = selectedRanges[0].bottomRight()
                leftColumn = topLeftIndex.column()
                rightColumn = bottomRightIndex.column()
                topRow = topLeftIndex.row()
                bottomRow = bottomRightIndex.row()
                if includeRowNumbers:
                   textClip = '\t'
                else:
                    textClip = ''
                if includeHeaders:
                    textClip = textClip+'\t'.join([self.__getHeaderValue(i) for i in xrange(leftColumn, rightColumn + 1)]) + '\n'
                for row in xrange(topRow, bottomRow + 1):
                    if includeRowNumbers:
                        textClip += str(row + 1) + '\t'
                    for column in xrange(leftColumn, rightColumn + 1):
                        try:
                            textClip += self.__getValue(row, column) + '\t'
                        except AttributeError:
                            textClip += '\t'
                    textClip = textClip[:-1] + '\n'
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)

        def keyPressEvent(self, e):
            # copy selection to clipboard
            if (e.modifiers() & Qt.ControlModifier):
                if e.key() == Qt.Key_C:
                    self.__copy(includeHeaders=False, includeRowNumbers=False)

        def __init__(self, *args):
            QTableView.__init__(self, *args)


    #
    # public
    #

    def setResult(self, result):
        if isinstance(result, list):
            modelResult = self.TableModel(result)
            self.tableResult.setModel(modelResult)
            self.box.setCurrentWidget(self.tableResult)
        else:
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
        palette = self.textResult.palette()
        palette.setColor(QPalette.Text, Qt.red)
        self.textResult.setPalette(palette)
        self.tableResult = self.TableResult()
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
    # drag and drop events
    #

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            for url in event.mimeData().urls():
                filename = str(url.toLocalFile())
                with open(filename, 'r') as fileScript:
                    script = fileScript.read()
                    self.addScript(filename, script)
        else:
            event.ignore()

    #
    # event
    #

    def __isEmptyEvent(self, empty):
        self.isEmpty.emit(empty)

    def __currentChangedEvent(self, index):
        editor = self.widget(index)
        if editor:
            if isinstance(editor, Editor):
                empty = editor.isTextEmpty()
                self.isEmpty.emit(empty)
            # it's result tab
            else:
                self.isEmpty.emit(True)

    def __tabCloseRequestedEvent(self, index):
        self.removeTab(index)
        if self.count() == 0:
            self.__isEmptyEvent(True)

    def __removeTabResult(self):
        for index in range(self.count()):
            widget = self.widget(index)
            if isinstance(widget, Result):
                self.removeTab(index)

    def __addTabResult(self):
        self.insertTab(0, self.result, 'RESULT')
        self.tabBar().setTabTextColor(0, Qt.red)
        self.setCurrentIndex(0)

    #
    # public
    #

    def setEnabledTabResult(self, enabled):
        self.__enabledTabResult = enabled
        if enabled:
            self.__addTabResult()
        else:
            self.__removeTabResult()

    def setResult(self, result):
        # set result
        self.result.setResult(result)
        if self.__enabledTabResult:
            self.__removeTabResult()
            self.__addTabResult()

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

    def currentScript(self):
        editor = self.currentWidget()
        script = None
        if editor:
            if isinstance(editor, Editor):
                script = editor.toPlainText()
                #script = unicode(script)
        return script

    #
    # init
    #

    def __init__(self):
        QTabWidget.__init__ (self)
        self.result = Result()
        self.countNewScript = 1
        self.setTabsClosable(True)
        self.setMovable(True)
        self.currentChanged.connect(self.__currentChangedEvent)
        self.tabCloseRequested.connect(self.__tabCloseRequestedEvent)
        self.__enabledTabResult = False
        self.setAcceptDrops(True)


class ToolBar(QToolBar):

    #
    # public
    #
    runQueryRequested = pyqtSignal()
    newQueryRequested = pyqtSignal()
    loadQueryRequested = pyqtSignal()
    showResultBelowRequested = pyqtSignal()
    showResultInTabRequested = pyqtSignal()
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
        if action == self.showResultBelow:
            self.showResultBelowRequested.emit()
        elif action == self.showResultInTab:
            self.showResultInTabRequested.emit()
        elif action == self.showResultToNewCsv:
            pass
        elif action == self.showColumnWizard:
            self.showColumnWizardRequested.emit()

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
        self.showResultBelow = QAction(self.tr('Result below'), self)
        self.showResultBelow.setCheckable(True)
        self.showResultBelow.setChecked(True)
        self.showResultToNewCsv = QAction(self.tr('Result to new csv'), self)
        self.showResultToNewCsv.setCheckable(True)
        self.showColumnWizard = QAction('Show column wizard', self)
        self.showColumnWizard.setCheckable(True)
        self.showColumnWizard.setChecked(True)

        # options button
        self.optionsMenu = QMenu()
        self.optionsMenu.addAction(self.showResultBelow)
        self.optionsMenu.addAction(self.showResultInTab)
        self.optionsMenu.addAction(self.showResultToNewCsv)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction(self.showColumnWizard)
        self.optionsMenu.triggered.connect(self.__toolBarActionTriggeredEvent)
        #
        actionGroup = QActionGroup(self.optionsMenu)
        self.showResultBelow.setActionGroup(actionGroup)
        self.showResultInTab.setActionGroup(actionGroup)
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
            tableCount = lib.querycsv.query_sqlite('SELECT COUNT(*) FROM "{0}"'.format(tableName), self.db)
            tableCount = tableCount[1][0]
            tableInfo = (tableName, tableCount, [field[1] for field in tableInfo[1:]])
            data.append(tableInfo)
        self.tables.setData(data)

    #
    # event
    #

    @waiting
    def __runQueryRequested(self):

        script = self.tab.currentScript()

        if script:

            # throw event to pass the CSV data calling the method setCsv
            self.runQueryRequested.emit()

            # test
            _array = [
            [u'name', u'number', u'color'],
            [u'cat', u'1', u'red'],
            [u'dog', u'2', u'green'],
            [u'bird', u'3', u'blue']
            ]
            lib.querycsv.import_array(self.db, _array, 'result', overwrite=True)
            #
            self.__setTables()
            #
            try:
                results = lib.querycsv.query_sqlite(script, self.db)
                if results:
                    self.result.setResult(results)
                    self.tab.setResult(results)
                else:
                    self.result.setResult('No results.')
                    self.tab.setResult('No results.')
            except Exception as ex:
                self.result.setResult(ex.message)
                self.tab.setResult(ex.message)


        else:
            self.result.setResult('')
            self.tab.setResult('')


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

    def __showResultBelowRequested(self):
        self.tab.setEnabledTabResult(False)
        self.result.setVisible(True)
        pass

    def __showResultInTabRequested(self):
        self.tab.setEnabledTabResult(True)
        self.result.setVisible(False)
        pass

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


##    from lib.helper import SimpleNamespace
##    def setCsvData2(self, documents):
##
##        for document in documents:
##            filename = os.path.basename(document.filename)
##            #timestamp = document.timestampLastChange
##            tableName, _ = os.path.splitext(filename)


    def setCsvData(self, documents):

## aqui antes tienes que eliminar la base de datos
## para no tener q hacerlo cada vez, hay que guardar en una variable en este widget un campo modificado.
## modificado=True al inicio, cuando entra aqui si es true, borra e inserta, si es false no hace nada.
## la variable pasa a True para cualquier operacion de csvs (1) add, modify, del csv
## tb puede servir una variable en cada csv tipo 'fecha ultima modificacion' <-- mejor.
## el problema viene si anado o quito un CSV... como controlo esto?
## y que tal algo con hashes? los objetos python tiene algo parecido a un hash?

        for document in documents:
            data = lib.helper.QStringMatrixToUnicode(document.arrayData())
            filename = os.path.basename(document.filename)
            tableName, _ = os.path.splitext(filename)
            timestamp = document.timestamp()
            print document.timestamp()

## no crear tabla si el csv no tiene datos

## columnas sin cabecera, columnas con cabecera repetida

## cuando elijes el nombre de la tabla, antes de add comprobar q no exista una tabla con mismo nombre.
## Si existe, entonces add un sufijo _1 _2 etc.

## aqui faltara algun funcion que elimine de 'tableName' caracteres invalidos para sqlite, si asi esta configurado
## sino se supone q con " o con [ ya sirve

            lib.querycsv.import_array(self.db, data, tableName, overwrite=True)

        #':memory:'
        #lib.querycsv.import_array(array, table_name, header=None, overwrite=False):
        #lib.querycsv.import_array(self.db, self.array, 'result')
        #results = query_sqlite('select * from result where name="dog"', self.db)


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
        self.tables = Tables()

        # events
        self.toolbar.runQueryRequested.connect(self.__runQueryRequested)
        self.toolbar.newQueryRequested.connect(self.__newQueryRequested)
        self.toolbar.loadQueryRequested.connect(self.__loadQueryRequested)
        self.toolbar.showColumnWizardRequested.connect(self.__showColumnWizardRequested)
        self.toolbar.showResultBelowRequested.connect(self.__showResultBelowRequested)
        self.toolbar.showResultInTabRequested.connect(self.__showResultInTabRequested)

        # tab
        self.tab.isEmpty.connect(self.__isEmptyEvent)
        self.tab.newScript()

        # edit splitter
        self.editSplitter = QSplitter(Qt.Vertical)
        self.editSplitter.addWidget(self.tab)
        self.editSplitter.addWidget(self.result)
        self.editSplitter.setStretchFactor(0, 5)
        self.editSplitter.setStretchFactor(1, 1)

        # main splitter
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
