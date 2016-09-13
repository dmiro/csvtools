from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.images_rc
import sys
from lib.config import config
from widgets.helpers.qfingertabwidget import QFingerTabWidget
from widgets.helpers.qcolorbox import QColorBox
from widgets.helpers.hline import HLine
from widgets.helpers.htitle import HTitle

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
        self.view_showColumnNumberHeaderRow.setChecked(config.view_showColumnNumberHeaderRow)
        self.view_showtools.setChecked(config.view_showtools)
        self.view_positiontools.setCurrentIndex(config.view_positiontools)
        self.view_showTitleTools.setChecked(config.view_showTitleTools)
        self.view_showborderdata.setChecked(config.view_showborderdata)
        self.view_colorborderdata.setColor(config.view_colorborderdata)
        self.view_widthborderdata.setCurrentIndex(config.view_widthborderdata - 1)
        self.view_showHighlightSections.setChecked(config.view_showHighlightSections)
        self.view_colorHighlightSections.setColor(config.view_colorHighlightSections)
        self.view_backgroundColorHighlightSections.setColor(config.view_backgroundColorHighlightSections)
        self.wizard_showToOpenFile.setChecked(config.wizard_showToOpenFile)
        self.wizard_showToSaveFile.setChecked(config.wizard_showToSaveFile)
        self.wizard_showSaveNewFile.setChecked(config.wizard_showSaveNewFile)
        self.wizard_showToReloadFile.setChecked(config.wizard_showToReloadFile)
        self.wizard_showToDropFile.setChecked(config.wizard_showToDropFile)
        self.wizard_loadAllLines.setChecked(config.wizard_loadAllLines)
        self.wizard_linesToLoad.setValue(config.wizard_linesToLoad)
        self.__checkDependenciesPreferences()

    def __saveConfig(self):
        config.config_restore = self.config_restore.checkState() == Qt.Checked
        config.recentfiles_check = self.recentfiles_check.checkState() == Qt.Checked
        config.recentfiles_maxEntries = self.recentfiles_maxEntries.value()
        config.tabbar_showclosebutton = self.tabbar_showclosebutton.checkState() == Qt.Checked
        config.tabbar_doubleclicktoclose = self.tabbar_doubleclicktoclose.checkState() == Qt.Checked
        config.tabbar_lock = self.tabbar_lock.checkState() == Qt.Checked
        config.view_headerrow = self.view_headerrow.checkState() == Qt.Checked
        config.view_showColumnNumberHeaderRow = self.view_showColumnNumberHeaderRow.checkState() == Qt.Checked
        config.view_showtools = self.view_showtools.checkState() == Qt.Checked
        config.view_positiontools = self.view_positiontools.currentIndex()
        config.view_showTitleTools = self.view_showTitleTools.checkState() == Qt.Checked
        config.view_showborderdata = self.view_showborderdata.checkState() == Qt.Checked
        config.view_colorborderdata = self.view_colorborderdata.color().rgb()
        config.view_widthborderdata = self.view_widthborderdata.currentIndex() + 1
        config.view_showHighlightSections = self.view_showHighlightSections.checkState() == Qt.Checked
        config.view_colorHighlightSections = self.view_colorHighlightSections.color().rgb()
        config.view_backgroundColorHighlightSections = self.view_backgroundColorHighlightSections.color().rgb()
        config.wizard_showToOpenFile = self.wizard_showToOpenFile.checkState() == Qt.Checked
        config.wizard_showToSaveFile = self.wizard_showToSaveFile.checkState() == Qt.Checked
        config.wizard_showSaveNewFile = self.wizard_showSaveNewFile.checkState() == Qt.Checked
        config.wizard_showToReloadFile = self.wizard_showToReloadFile.checkState() == Qt.Checked
        config.wizard_showToDropFile = self.wizard_showToDropFile.checkState() == Qt.Checked
        config.wizard_loadAllLines = self.wizard_loadAllLines.checkState() == Qt.Checked
        config.wizard_linesToLoad = self.wizard_linesToLoad.value()

    def __acceptDialog(self):
        self.__saveConfig()
        self.accept()

    def __checkDependenciesPreferences(self):
        # 'show border data' dependencies
        checked = self.view_showborderdata.checkState() == Qt.Checked
        self.view_colorborderdata.setEnabled(checked)
        self.view_widthborderdata.setEnabled(checked)
        # 'Load all lines' dependencies
        checked = self.wizard_loadAllLines.checkState() == Qt.Checked
        self.wizard_linesToLoad.setEnabled(not checked)

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
        tabs = QTabWidget()
        tabs.setTabBar(QFingerTabWidget(width=110, height=25))
        tabs.setTabPosition(QTabWidget.West)

        # General
        general = QWidget()
        tabs.addTab(general, self.tr('General'))
        self.config_language = QComboBox()
        grid = QFormLayout(parent=general)
        grid.addRow(self.tr('Language'), self.config_language)

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
        self.view_showColumnNumberHeaderRow = QCheckBox('')
        self.view_showtools = QCheckBox('')
        self.view_positiontools = QComboBox()
        self.view_showTitleTools = QCheckBox('')
        self.view_positiontools.addItems(['Left', 'Right', 'Top', 'Bottom'])
        self.view_showborderdata = QCheckBox('')
        self.view_showborderdata.clicked.connect(self.__checkDependenciesPreferences)
        self.view_colorborderdata = QColorBox(defaultColor=Qt.red)
        self.view_widthborderdata = QComboBox()
        self.view_widthborderdata.addItems(['1', '2', '3', '4', '5'])
        self.view_showHighlightSections = QCheckBox('')
        self.view_colorHighlightSections = QColorBox(defaultColor=Qt.white)
        self.view_backgroundColorHighlightSections = QColorBox(defaultColor=Qt.black)
        grid = QFormLayout(parent=backup)
        grid.addRow(HTitle('Header Row'))
        grid.addRow(self.tr('Show to open file'), self.view_headerrow)
        grid.addRow(self.tr('Show column number'), self.view_showColumnNumberHeaderRow)
        grid.addRow(HTitle(text = 'Tools', marginTop = 15))
        grid.addRow(self.tr('Show to start'), self.view_showtools)
        grid.addRow(self.tr('Initial position'), self.view_positiontools)
        grid.addRow(self.tr('Show title'), self.view_showTitleTools)
        grid.addRow(HTitle(text = 'Border Data', marginTop = 15))
        grid.addRow(self.tr('Show'), self.view_showborderdata)
        grid.addRow(self.tr('Border color'), self.view_colorborderdata)
        grid.addRow(self.tr('Border width'), self.view_widthborderdata)
        grid.addRow(HTitle(text = 'Highlight Sections', marginTop = 15))
        grid.addRow(self.tr('Show'), self.view_showHighlightSections)
        grid.addRow(self.tr('Color'), self.view_colorHighlightSections)
        grid.addRow(self.tr('Background color'), self.view_backgroundColorHighlightSections)

        # Format Wizard
        backup = QWidget()
        tabs.addTab(backup, self.tr('CSV Format Wizard'))
        self.wizard_showToOpenFile = QCheckBox()
        self.wizard_showToSaveFile = QCheckBox()
        self.wizard_showSaveNewFile = QCheckBox()
        self.wizard_showToReloadFile = QCheckBox()
        self.wizard_showToDropFile = QCheckBox()
        self.wizard_loadAllLines = QCheckBox()
        self.wizard_loadAllLines.clicked.connect(self.__checkDependenciesPreferences)
        self.wizard_linesToLoad = QSpinBox()
        self.wizard_linesToLoad.setRange(1, 100000)
        grid = QFormLayout(parent=backup)
        grid.addRow(HTitle('Show when..'))
        grid.addRow(self.tr('Open a file'), self.wizard_showToOpenFile)
        grid.addRow(self.tr('Save a file'), self.wizard_showToSaveFile)
        grid.addRow(self.tr('Save a NEW file'), self.wizard_showSaveNewFile)
        grid.addRow(self.tr('Reload a file'), self.wizard_showToReloadFile)
        grid.addRow(self.tr('Drag && drop a file'), self.wizard_showToDropFile)
        grid.addRow(HTitle(text = 'Lines to Load', marginTop = 15))
        grid.addRow(self.tr('Load all lines'), self.wizard_loadAllLines)
        grid.addRow(self.tr('Num. lines'), self.wizard_linesToLoad)

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
        self.setFixedSize(400, 450)





