from PyQt4.QtCore import *
from PyQt4.QtGui import *

import lib.images_rc
import lib.querycsv

# https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
# http://python.jpvweb.com/mesrecettespython/doku.php?id=pyqt4_colorisation_syntaxe_qtextedit

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]
    keywords = [
        'ABORT','COLUMN','ESCAPE','INSERT','ORDER','TABLE',
        'ACTION','COMMIT','EXCEPT','INSTEAD','OUTER','TEMP',
        'ADD','CONFLICT','EXCLUSIVE','INTERSECT','PLAN','TEMPORARY',
        'AFTER','CONSTRAINT','EXISTS','INTO','PRAGMA','THEN',
        'ALL','CREATE','EXPLAIN','IS','PRIMARY','TO',
        'ALTER','CROSS','FAIL','ISNULL','QUERY','TRANSACTION',
        'ANALYZE','CURRENT_DATE','FOR','JOIN','RAISE','TRIGGER',
        'AND','CURRENT_TIME','FOREIGN','KEY','RECURSIVE','UNION',
        'AS','CURRENT_TIMESTAMP','FROM','LEFT','REFERENCES','UNIQUE',
        'ASC','DATABASE','FULL','LIKE','REGEXP','UPDATE',
        'ATTACH','DEFAULT','GLOB','LIMIT','REINDEX','USING',
        'AUTOINCREMENT','DEFERRABLE','GROUP','MATCH','RELEASE','VACUUM',
        'BEFORE','DEFERRED','HAVING','NATURAL','RENAME','VALUES',
        'BEGIN','DELETE','IF','NO','REPLACE','VIEW',
        'BETWEEN','DESC','IGNORE','NOT','RESTRICT','VIRTUAL',
        'BY','DETACH','IMMEDIATE','NOTNULL','RIGHT','WHEN',
        'CASCADE','DISTINCT','IN','NULL','ROLLBACK','WHERE',
        'CASE','DROP','INDEX','OF','ROW','WITH',
        'CAST','EACH','INDEXED','OFFSET','SAVEPOINT','WITHOUT',
        'CHECK','ELSE','INITIALLY','ON','SELECT',
        'COLLATE','END','INNER','OR','SET',
        'TEXT', 'INTEGER', 'REAL', 'NUMERIC' 'NONE', 'BLOB','TRUE', 'FALSE'
        ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '--' until a newline
            (r'--[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat, Qt.CaseInsensitive), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class Editor(QPlainTextEdit):

    def __init__(self):
        QPlainTextEdit.__init__ (self)
        self.highlight = PythonHighlighter(self.document())


class Tab(QTabWidget):

    #
    # public
    #

    def newScript(self):
        editor = Editor()
        self.addTab(editor, 'script {0}'.format(self.countNewScript))
        self.countNewScript = self.countNewScript + 1

    #
    # init
    #

    def __init__(self):
        QTabWidget.__init__ (self)
        self.countNewScript = 1
        self.setTabsClosable(True)

class ToolBar(QToolBar):

    #
    # public
    #

    runQueryRequested = pyqtSignal()

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
            pass

        # actions
        elif action == self.runQueryAction:
            self.runQueryRequested.emit()
        elif action == self.newQueryAction:
            pass
        elif action == self.loadQueryAction:
            pass
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
        self.showResultToNewCsv = QAction(self.tr('Result to new csv'), self)
        self.showResultToNewCsv.setCheckable(True)
        self.showColumnWizard = QAction('Show column wizard', self)
        self.showColumnWizard.setCheckable(True)

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
        self.showResultInTab.setChecked(True)
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
        [u'name', u'number'],
        [u'cat', u'1'],
        [u'dog', u'2'],
        [u'bird', u'3']
        ]
        lib.querycsv.import_array(self.db, _array, 'result', overwrite=True)
        results = lib.querycsv.query_sqlite(script, self.db)
        print results
        # test
        self.runQueryRequested.emit()

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

        # events
        self.toolbar.runQueryRequested.connect(self.__runQueryRequested)

        # splitter
        self.splitter= QSplitter(Qt.Horizontal)

        #
        self.tab.newScript()
        self.tab.newScript()
        self.b = QLabel('adios')
        self.splitter.addWidget(self.tab)
        self.splitter.addWidget(self.b)

        # main layout
        layout= QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.splitter)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)
        self.setWindowTitle(self.tr('Query Csv'))
