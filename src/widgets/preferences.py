from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.images_rc
import sys
from lib.config import config
from widgets.helpers.qfingertabwidget import QFingerTabWidget
from widgets.helpers.qcolorbox import QColorBox

class Preferences(QDialog):

    #
    # private
    #

    def __loadConfig(self):
        self.config_restore.setChecked(config.config_restore)
        self.recentfiles_check.setChecked(config.recentfiles_check)
        self.recentfiles_maxEntries.setValue(config.recentfiles_maxEntries)
        self.tabbar_showclosebutton.setChecked(config.tabbar_showclosebutton)
        self.tabbar_doubleclicktoclose.setChecked(config.tabbar_doubleclicktoclose)
        self.tabbar_lock.setChecked(config.tabbar_lock)
        self.view_headerrow.setChecked(config.view_headerrow)
        self.view_showborderdata.setChecked(config.view_showborderdata)
        self.view_colorborderdata.setColor(config.view_colorborderdata)

    def __saveConfig(self):
        config.config_restore = self.config_restore.checkState() == Qt.Checked
        config.recentfiles_check = self.recentfiles_check.checkState() == Qt.Checked
        config.recentfiles_maxEntries = self.recentfiles_maxEntries.value()
        config.tabbar_showclosebutton = self.tabbar_showclosebutton.checkState() == Qt.Checked
        config.tabbar_doubleclicktoclose = self.tabbar_doubleclicktoclose.checkState() == Qt.Checked
        config.tabbar_lock = self.tabbar_lock.checkState() == Qt.Checked
        config.view_headerrow = self.view_headerrow.checkState() == Qt.Checked
        config.view_showborderdata = self.view_showborderdata.checkState() == Qt.Checked
        config.view_colorborderdata = self.view_colorborderdata.color().rgb()

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
        tabs.setTabBar(QFingerTabWidget(width=75, height=25))
        tabs.setTabPosition(QTabWidget.West)

        # General
        general = QWidget()
        tabs.addTab(general, self.tr('General'))
        self.config_language = QComboBox()
        self.config_autodetect = QCheckBox('')
        grid = QFormLayout(parent=general)
        grid.addRow(self.tr('Language'), self.config_language)
        grid.addRow(self.tr('Detect format'), self.config_autodetect)

        # Tab bar
        tabBar = QWidget()
        tabs.addTab(tabBar, self.tr('Tab Bar'))
        self.tabbar_showclosebutton = QCheckBox('')
        self.tabbar_doubleclicktoclose = QCheckBox('')
        self.tabbar_lock = QCheckBox('')
        grid = QFormLayout(parent=tabBar)
        grid.addRow(self.tr('Show close button on each tab'), self.tabbar_showclosebutton)
        grid.addRow(self.tr('Double click to close document'), self.tabbar_doubleclicktoclose)
        grid.addRow(self.tr('Lock'), self.tabbar_lock)

        # Recent Files
        recentFiles = QWidget()
        tabs.addTab(recentFiles, self.tr('Recent Files'))
        self.recentfiles_check= QCheckBox('')
        self.recentfiles_maxEntries = QSpinBox()
        self.recentfiles_maxEntries.setRange(0, 100)
        grid = QFormLayout(parent=recentFiles)
        grid.addRow(self.tr('Check at launch time'), self.recentfiles_check)
        grid.addRow(self.tr('Max. number of entries'), self.recentfiles_maxEntries)

        # Backup
        backup = QWidget()
        tabs.addTab(backup, self.tr('Backup'))
        self.config_restore = QCheckBox('')
        grid = QFormLayout(parent=backup)
        grid.addRow(self.tr('Restore Session'), self.config_restore)

        # View
        backup = QWidget()
        tabs.addTab(backup, self.tr('View'))
        self.view_headerrow = QCheckBox('')
        self.view_showborderdata = QCheckBox('')
        ##self.view_showborderdata.clicked
        self.view_colorborderdata = QColorBox(defaultColor=Qt.red)
        ##self.view_colorborderdata.setEnabled(False)
        grid = QFormLayout(parent=backup)
        grid.addRow(self.tr('Header Row'), self.view_headerrow)
        grid.addRow(self.tr('Show border data'), self.view_showborderdata)
        grid.addRow(self.tr('Color border data'), self.view_colorborderdata)

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
        self.setWindowTitle(self.tr('Preferences'))
        self.setFixedSize(400, 200)





