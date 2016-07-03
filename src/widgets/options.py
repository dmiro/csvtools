from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.images_rc
import sys
from lib.config import config
from widgets.helpers.qfingertabwidget import QFingerTabWidget

class Options(QDialog):

    #
    # private
    #

    def __loadConfig(self):
         self.config_restore.setChecked(config.config_restore)

    def __saveConfig(self):
        config.config_restore = self.config_restore.checkState() == Qt.Checked

    def __acceptDialog(self):
        self.__saveConfig()
        self.accept()

    def __addButtonBox(self):
        acceptButton = QPushButton(self.tr('Accept'), self)
        acceptButton.setIcon(QIcon(':images/accept.png'))
        cancelButton = QPushButton(self.tr('Cancel'), self)
        cancelButton.setIcon(QIcon(':images/cancel.png'))
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(self.__acceptDialog)
        buttonBox.rejected.connect(lambda: self.reject())
        return buttonBox

    def __addTabOptions(self):
        # tab widget
        tabs = QTabWidget()
        tabs.setTabBar(QFingerTabWidget(width=100, height=25))
        tabs.setTabPosition(QTabWidget.West)

        # general
        general = QWidget()
        tabs.addTab(general, self.tr('General'))
        self.config_language = QComboBox()
        self.config_autodetect = QCheckBox('')
        grid = QFormLayout(parent=general)
        grid.addRow(self.tr('Language'), self.config_language)
        grid.addRow(self.tr('Detect format'), self.config_autodetect)

        # backup
        backup = QWidget()
        tabs.addTab(backup, self.tr('Backup'))
        self.config_restore = QCheckBox('')
        grid = QFormLayout(parent=backup)
        grid.addRow(self.tr('Restore Session'), self.config_restore)
        return tabs

    #
    # init
    #

    def __init__(self, *args):
        QDialog.__init__(self, *args)

        # widgets
        self.tabOptions = self.__addTabOptions()
        self.buttonBox = self.__addButtonBox()

        # layout
        main = QVBoxLayout()
        main.addWidget(self.tabOptions)
        main.addWidget(self.buttonBox)

        # load config
        self.__loadConfig()

        # main
        self.setLayout(main)
        self.setWindowTitle(self.tr('Options'))
        self.setFixedSize(400, 200)





