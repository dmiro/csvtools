from PyQt4.QtCore import *
from PyQt4.QtGui import *

import lib.images_rc

class ToolBar(QToolBar):

    #
    # event
    #

    def __menuOptionClickedEvent(self):
        heightWidget = self.optionsButton.height()
        point = self.optionsButton.mapToGlobal(QPoint(0, heightWidget))
        self.optionsMenu.exec_(point)

    def __toolBarActionTriggeredEvent(self, action):
        if action == self.showResultInTab:
            pass
        elif action == self.showColumnWizard:
            pass

    #
    # init
    #

    def __init__(self):
        QToolBar.__init__ (self)

        # actions
        self.newQueryAction = QAction(QIcon(':images/refresh.png'), self.tr('New script'), self)
        self.runQueryAction = QAction(QIcon(':images/refresh.png'), self.tr('Run script'), self)
        self.loadQueryAction = QAction(QIcon(':images/refresh.png'), self.tr('Load script'), self)
        self.saveQueryAction = QAction(QIcon(':images/refresh.png'), self.tr('Save script'), self)
        self.resultToCsvAction = QAction(QIcon(':images/refresh.png'), self.tr('Result to new csv'), self)
        self.showResultInTab = QAction(self.tr('Result in tab'), self)
        self.showResultInTab.setCheckable(True)
        self.showColumnWizard = QAction('Show column wizard', self)
        self.showColumnWizard.setCheckable(True)

        # options button
        self.optionsMenu = QMenu()
        self.optionsMenu.addAction(self.showResultInTab)
        self.optionsMenu.addAction(self.showColumnWizard)
        self.optionsMenu.triggered.connect(self.__toolBarActionTriggeredEvent)
        self.optionsButton = QToolButton()
        self.optionsButton.setMenu(self.optionsMenu)
        self.optionsButton.setIcon(QIcon(':images/filteroptions.png'))
        self.optionsButton.setStatusTip(self.tr('Options'))
        self.optionsButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.optionsButton.clicked.connect(self.__menuOptionClickedEvent)

        # toolbar
        self.setIconSize(QSize(16, 16))
        self.addAction(self.newQueryAction)
        self.addAction(self.runQueryAction)
        self.addAction(self.loadQueryAction)
        self.addAction(self.saveQueryAction)
        self.addAction(self.resultToCsvAction)
        self.addSeparator()
        self.addWidget(self.optionsButton)
        self.actionTriggered.connect(self.__toolBarActionTriggeredEvent)


class QQueryCsv(QDialog):

    #
    # private
    #

    #
    # slots
    #

    ##def __groupBoxClickedSlot(self):
    ##    pass

    #
    # widgets
    #

    ##def __addButtonBox(self):
    ##    pass

    #
    # public
    #

    #
    # init
    #

    def __init__(self, *args):
        QDialog.__init__ (self, *args)

        # widgets
        self.toolbar = ToolBar()

        # main layout
        layout= QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)
        self.setWindowTitle(self.tr('Query Csv'))
