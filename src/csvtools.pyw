# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.about import QAbout
from widgets.options import Options
from widgets.report import QReport
from widgets.importwiz import QImportWiz
from widgets.csvm import QCsv
from widgets.explorer import QExplorer
from widgets.status import QStatus
from widgets.search import QSearch
from widgets.opencsvfiledialog import QOpenCsvFileDialog
from widgets.csvwiz import QCsvWiz
import lib.document
import lib.exports
import lib.imports
from lib.config import config
from lib.helper import waiting, get_excel_sheets, QStringToUnicode
import lib.images_rc
import sys
import os


class MainWindow(QMainWindow):

    #
    # private
    #

    @waiting
    def addCsv(self, file_, insertIndex=-1):
        file_ = str(file_)
        for index in range(self.tab.count()):
            if file_ in self.tab.tabToolTip(index):
                self.tab.setCurrentIndex(index)
                return
        hook = file_.rfind('#')
        if hook > -1:
            sheetname = file_[hook+1:]
            excelfile = file_[:hook]
            xslDoc = lib.document.Xsl(excelfile, sheetname)
            xslDoc.load()
            csv = QCsv(xslDoc)
        else:
            csvDoc = lib.document.Csv(file_)
            csvDoc.load()
            csv = QCsv(csvDoc)
        csv.selectionChanged_.connect(self.csvSelectionChangedEvent)
        csv.contextMenuRequested.connect(self.csvcontextMenuRequestedEvent)
        filename = os.path.basename(file_)
        if insertIndex > -1:
            index = self.tab.insertTab(insertIndex, csv, filename)
        else:
            index = self.tab.addTab(csv, filename)
        self.tab.setTabToolTip(index, file_)
        self.tab.setCurrentIndex(index)
        self.addRecentFile(file_)
        self.refreshRecentFileActions()
        self.saveSessionFile()

    @waiting
    def reload(self, csv):
        csv.document.load()

    def openCsv(self, filenames):
        if filenames:
            if isinstance(filenames, QString):
                filenames = str(filenames)
            if isinstance(filenames, basestring):
                filenames = [filenames]
            warnings = []
            for filename in filenames:
                try:
                    self.addCsv(filename)
                except IOError:
                    warnings.append('No such file {0}'.format(filename))
                except Exception, e:
                    warnings.append('Error opening file {0}: {1}'.format(filename, e))
            if warnings:
                report = QReport(warnings)
                report.exec_()

    def emptyRecentFiles(self):
        """empty recent files and refresh menu"""
        config.file_recent = []
        self.refreshRecentFileActions()

    def restoreLastSession(self):
        """retrieve files the last session"""
        self.openCsv(config.file_files)

    def refreshRecentFileActions(self):
        """update recent files menu"""
        self.recent.clear()
        for index, recent in enumerate(config.file_recent):
            action = QAction("%d. %s" % (index+1,recent), self)
            action.setStatusTip("%s %s" % (self.tr('Open'), recent))
            action.triggered[()].connect(lambda recent=recent: self.openCsv(recent))
            self.recent.addAction(action)
        self.recent.addSeparator()
        empty = QAction(self.tr('Empty'), self)
        empty.setStatusTip(self.tr('Empty recent list'))
        empty.triggered.connect(self.emptyRecentFiles)
        empty.setDisabled(len(config.file_recent) == 0)
        self.recent.addAction(empty)

    def addRecentFile(self, file_):
        """add in config file the last opened file"""
        file_recent = config.file_recent 
        if file_ in file_recent:
            file_recent.remove(file_)
        file_recent.insert(0, file_)
        config.file_recent = file_recent[0:20]

    def saveSessionFile(self):
        """save in config file the session files"""
        config.file_files = [str(self.tab.tabToolTip(index)) for index in range(self.tab.count())]

    def searchText(self, text, tabIndex, matchMode, matchCaseOption):
        csv = self.tab.widget(tabIndex)
        tabText = self.tab.tabText(tabIndex)
        tabToolTip = self.tab.tabToolTip(tabIndex)
        result = csv.search(text, matchMode, matchCaseOption)
        if len(result) > 0:
            return {'tabText':tabText, 'tabToolTip': tabToolTip, 'result':result}

    def setMenuDisabled(self, menu, disabled):
        for action in menu.actions():
            if not action.menu():
                action.setDisabled(disabled)
  
    def setEditMenuDisabled(self, disabled):
        self.setMenuDisabled(self.editMenu, disabled)
        self.setMenuDisabled(self.copySpecialMenu, disabled)
        self.setMenuDisabled(self.copyToPythonMenu, disabled)

    #
    # drag and drop events
    #

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            #event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            #event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            #links = []
            for url in event.mimeData().urls():
                filename = str(url.toLocalFile())
                _, fileExtension = os.path.splitext(filename)
                if fileExtension == '.xls' or fileExtension == '.xlsx':
                    self.importExcelAction(filename)
                else:
                    self.openCsv(filename)
        else:
            event.ignore()

    #
    # file menu action methods
    #

    def importExcelAction(self, filename):
        filename = str(filename)
        sheets = get_excel_sheets(filename)
        im = QImportWiz(sheets)
        if im.exec_() == QDialog.Accepted:
            sheets = im.sheets()
            filenames = ['{0}#{1}'.format(filename, sheet) for sheet in sheets]
            self.openCsv(filenames)

    def importDialogAction(self):
        """import xls/xlsx dialog"""
        filename = QFileDialog.getOpenFileName(self, self.tr('Import file'), '', "Excel Files (*.xlsx *.xls)")
        if filename:
            self.importExcelAction(filename)

    def openDialogAction(self):
        """open csv dialog"""
        filename, useWizard = QOpenCsvFileDialog.getOpenFileName(self)
        if filename:
            # use csv wizard
            if useWizard:
               csvWiz = QCsvWiz(filename=filename)
               csvWiz.exec_()
            # open csv with standard parameters
            else:
                filename = str(filename)
                self.openCsv(filename)

    def exitDialogAction(self):
        """exit dialog"""
        quitmsg = self.tr('Are you sure you want to exit?')
        reply = QMessageBox.question(self, self.tr('Message'), quitmsg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            exit()

    def closeFileAction(self):
        """close current file"""
        index = self.tab.currentIndex()
        if index > -1:
            self.tabCloseRequestedEvent(index)

    def closeAllFilesAction(self):
        """close all files"""
        self.tab.clear()
        self.saveSessionFile()

    def closeAllButThisFilesAction(self):
        """close all files except current file"""
        csv = self.tab.currentWidget()
        index = self.tab.currentIndex()
        tabToolTip = self.tab.tabToolTip(index)
        tabText = self.tab.tabText(index)
        self.tab.clear()
        index = self.tab.addTab(csv, tabText)
        self.tab.setTabToolTip(index, tabToolTip)
        self.saveSessionFile()

    def reloadFileAction(self):
        """reload current file"""
        csv = self.tab.currentWidget()
        if csv:
            self.reload(csv)

    def filePathToClipboardAction(self):
        """copy to clipboard current file path"""
        index = self.tab.currentIndex()
        file_ = self.tab.tabToolTip(index)
        clipboard = QApplication.clipboard()
        clipboard.setText(file_)

    def allFilePathsToClipboardAction(self):
        """add all file path to clipboard"""
        # retrieve path files
        files = []
        for index in range(self.tab.count()):
            file_ = str(self.tab.tabToolTip(index))
            hook = file_.rfind('#')
            if hook > -1:
                file_ = file_[:hook]
            files.append(file_)
        # remove duplicates
        files = set(files)
        # copy path files to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(files))

    #
    # edit menu action methods
    #

    def editAction(self, action):
        csv = self.tab.currentWidget()
        if csv:
            textClip = None

            # copy to clipboard action
            if action == self.copyToClipboard:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=False)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toClipboard(matrix)
            # copy with Column Name(s) action
            elif action == self.copyWithHeaderColumnsToClipboard:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toClipboard(matrix)
            # copy Column Name(s) action
            elif action == self.copyHeaderColumnsToClipboard:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toClipboard([matrix[0]])
            # copy As JSON action
            elif action == self.copyAsJSON:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toJSON(matrix)
            # copy As Delimited action
            elif action == self.copyAsDelimited:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toDelimitied(matrix)
            # copy As Delimited action
            elif action == self.copyAsXML:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toXML(matrix)
            # copy As Text action
            elif action == self.copyAsText:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toText(matrix)
            # copy As HTML action
            elif action == self.copyAsHTML:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toHTML(matrix)
            # copy Python Source Code As TEXT action
            elif action == self.copyPythonAsText:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toPythonText(matrix)
            # copy Python Source Code As TUPLE action
            elif action == self.copyPythonAsTuple:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toPythonTuple(matrix)
            # copy Python Source Code As LIST action
            elif action == self.copyPythonAsList:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toPythonList(matrix)
            # copy Python Source Code As DICT action
            elif action == self.copyPythonAsDict:
                matrix = csv.selectedIndexesToRectangularArea(includeHeaderRows=True)
                if matrix:
                    textClip = lib.exports.ClipboardFormat.toPythonDict(matrix)

            # at last copy result to clipboard
            if textClip:
                clipboard = QApplication.clipboard()
                clipboard.setText(textClip, mode=QClipboard.Clipboard)
                return
            
            # paste from clipboard action
            if action == self.pasteFromClipboard:
                clipboard = QApplication.clipboard()
                textClip = clipboard.text()
                matrix = lib.imports.ClipboardFormat.toMatrix(textClip)
                csv.rectangularAreaToSelectedIndex(matrix)


    #
    # tool menu action methods
    #

    def explorerToolAction(self):
        self.toolTab.setCurrentIndex(0)

    def searchToolAction(self):
        self.toolTab.setCurrentIndex(1)

    #
    # config menu action methods
    #

    def optionsDialogAction(self):
        """show options dialog"""
        dialog = Options(self)
        dialog.exec_()

    def restoreSessionConfigAction(self):
        config.config_restore = not config.config_restore
        self.restoreSession.setChecked(config.config_restore)

    def headerRowConfigAction(self):
        config.config_headerrow = not config.config_headerrow

    #
    # help menu action methods
    #

    def aboutDialogAction(self):
        """show about dialog"""
        dialog = QAbout(self)
        dialog.exec_()


    #
    # event
    #

    def csvSelectionChangedEvent(self):
        csv = self.tab.currentWidget()
        if csv:
            self.setEditMenuDisabled(len(csv.selectedIndexes()) == 0)
            self.statusBar.setValues(csv.linesValue(), csv.columnsValue(), csv.sizeValue(),
                                    csv.modifiedValue(), csv.itemsValue(), csv.averageValue(),
                                    csv.sumValue())
        else:
            self.setEditMenuDisabled(True)
            self.statusBar.setValues(None, None, None, None, None, None, None)

    def csvcontextMenuRequestedEvent(self, selectedIndexes, globalPoint):
        self.editMenu.exec_(globalPoint)

    def statusBarChangedFontSizeEvent(self, fontSize):
        for index in range(self.tab.count()):
            csv = self.tab.widget(index)
            csv.setPointSize(fontSize)
            csv.resizeRowsToContents()
        csv = self.tab.currentWidget()
        csv.setPointSize(fontSize)
        csv.resizeRowsToContents()

    def tabCloseRequestedEvent(self, index):
        """event when a tab is closed: remove tab & update config"""
        file_ = self.tab.tabToolTip(index)
        self.tab.removeTab(index)
        self.saveSessionFile()

    def tabCurrentChangedEvent(self, index=0):
        """event when a selected tab is changed"""
        csv = self.tab.currentWidget()
        if csv:
            self.closeAllButThis.setDisabled(False)
            self.closeAllFiles.setDisabled(False)
            self.closeFile.setDisabled(False)
            self.filePathToClipboard.setDisabled(False)
            self.allFilePathsToClipboard.setDisabled(False)
            self.setEditMenuDisabled(len(csv.selectedIndexes()) == 0)
            self.statusBar.setValues(csv.linesValue(), csv.columnsValue(), csv.sizeValue(),
                                     csv.modifiedValue(), csv.itemsValue(), csv.averageValue(),
                                     csv.sumValue())

        else:
            self.closeAllButThis.setDisabled(True)
            self.closeAllFiles.setDisabled(True)
            self.closeFile.setDisabled(True)
            self.filePathToClipboard.setDisabled(True)
            self.allFilePathsToClipboard.setDisabled(True)
            self.setEditMenuDisabled(True)
            self.statusBar.setValues(None, None, None, None, None, None, None)

    def tabBarcustomContextMenuRequestedEvent(self, point):
        tab = self.tab.tabBar()
        # set current tab index
        tabIndex = tab.tabAt(point)
        if self.tab.currentIndex() != tabIndex:
            self.tab.setCurrentIndex(tabIndex)
        # make and show menu
        menu = QMenu("Tab Menu")
        menu.addAction(self.reloadFile)
        menu.addAction(self.closeFile)
        menu.addAction(self.closeAllFiles)
        menu.addAction(self.closeAllButThis)
        menu.addSeparator()
        menu.addAction(self.filePathToClipboard)
        menu.exec_(tab.mapToGlobal(point))

    def tabBartabMovedEvent(self, from_, to):
        self.saveSessionFile()

    @waiting
    def searchSearchClickedEvent(self, text):
        data = []
        matchMode = self.search.matchModeOption()
        matchCaseOption = self.search.matchCaseOption()
        findAllDocuments = self.search.findAllDocumentsOption()
        if findAllDocuments:
            for index in range(self.tab.count()):
                result = self.searchText(text, index, matchMode, matchCaseOption)
                if result:
                    data.append(result)
        else:
            index = self.tab.currentIndex()
            result = self.searchText(text, index, matchMode, matchCaseOption)
            if result:
                    data.append(result)
        self.search.setResult(data)

    def searchResultClickedEvent(self, file_, row, column, value):
        file_ = str(file_)
        for index in range(self.tab.count()):
            if file_ in self.tab.tabToolTip(index):
                self.tab.setCurrentIndex(index)
        csv = self.tab.currentWidget()
        csv.setSelectCell(row, column)

    def explorerClickedFileEvent(self, filename):
        filename = str(filename)
        _, fileExtension = os.path.splitext(filename)
        if fileExtension == '.xls' or fileExtension == '.xlsx':
            self.importExcelAction(filename)
        else:
            self.openCsv(filename)

    #
    # widgets
    #

    def addFileMenu(self):
        """add FILE menu"""

        #open file action
        self.openFile = QAction(QIcon(':images/open.png'), self.tr('&Open'), self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip(self.tr('Open Csv File'))
        self.openFile.triggered.connect(self.openDialogAction)

        #import file action
        self.importFile = QAction(QIcon(':images/import.png'), self.tr('Import'), self)
        self.importFile.setShortcut('Ctrl+I')
        self.importFile.setStatusTip(self.tr('Import Excel File'))
        self.importFile.triggered.connect(self.importDialogAction)

        #reload file action
        self.reloadFile = QAction(QIcon(':images/reload.png'), self.tr('Reload from Disk'), self)
        self.reloadFile.setShortcut('Ctrl+R')
        self.reloadFile.setStatusTip(self.tr('Reload File from Disk'))
        self.reloadFile.triggered.connect(self.reloadFileAction)

        #close file action
        self.closeFile = QAction(QIcon(':images/close.png'), self.tr('Close'), self)
        self.closeFile.setShortcut('Ctrl+W')
        self.closeFile.setStatusTip(self.tr('Close File'))
        self.closeFile.triggered.connect(self.closeFileAction)

        #close all files action
        self.closeAllFiles = QAction(self.tr('Close All'), self)
        self.closeAllFiles.setStatusTip(self.tr('Close All Files'))
        self.closeAllFiles.triggered.connect(self.closeAllFilesAction)

        #Close All BUT This action
        self.closeAllButThis = QAction(self.tr('Close All BUT This'), self)
        self.closeAllButThis.setStatusTip(self.tr('Close All BUT This'))
        self.closeAllButThis.triggered.connect(self.closeAllButThisFilesAction)

        #File Path to Clipboard action
        self.filePathToClipboard = QAction(self.tr('File Path to Clipboard'), self)
        self.filePathToClipboard.setStatusTip(self.tr('File Path to Clipboard'))
        self.filePathToClipboard.triggered.connect(self.filePathToClipboardAction)

        #File Path to Clipboard action
        self.allFilePathsToClipboard = QAction(self.tr('All File Paths to Clipboard'), self)
        self.allFilePathsToClipboard.setStatusTip(self.tr('All File Paths to Clipboard'))
        self.allFilePathsToClipboard.triggered.connect(self.allFilePathsToClipboardAction)

        #exit action
        self.exitApp = QAction(QIcon(':images/exit.png'), self.tr('E&xit'), self)
        self.exitApp.setShortcut('Ctrl+X')
        self.exitApp.setStatusTip(self.tr('Exit'))
        self.exitApp.triggered.connect(self.exitDialogAction)

        #file menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(self.tr('&File'))
        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.importFile)
        fileMenu.addAction(self.reloadFile)
        fileMenu.addAction(self.closeFile)
        fileMenu.addAction(self.closeAllFiles)
        fileMenu.addAction(self.closeAllButThis)
        self.recent = fileMenu.addMenu(self.tr('Recent Files'))
        self.refreshRecentFileActions()
        fileMenu.addSeparator()
        self.copyToClipboardMenu = fileMenu.addMenu(self.tr('Copy to Clipboard'))
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitApp)

        #clipboard submenu
        self.copyToClipboardMenu.addAction(self.filePathToClipboard)
        self.copyToClipboardMenu.addAction(self.allFilePathsToClipboard)

    def addEditMenu(self):
        """add EDIT menu"""

        # edit menu
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu(self.tr('Edit'))
        self.copyToClipboard = self.editMenu.addAction(self.tr('&Copy'))
        self.copyToClipboard.setShortcut('Ctrl+C')
        self.pasteFromClipboard = self.editMenu.addAction(self.tr('Paste'))
        self.pasteFromClipboard.setShortcut('Ctrl+V')
        self.editMenu.addSeparator()
        self.copySpecialMenu = self.editMenu.addMenu(self.tr('Copy Special'))
        self.copyToSourceCodeMenu = self.editMenu.addMenu(self.tr('Copy to Source Code'))
        self.copyToPythonMenu = self.copyToSourceCodeMenu.addMenu(self.tr('Python'))

        # copy special submenu
        self.copyWithHeaderColumnsToClipboard = self.copySpecialMenu.addAction(self.tr('Copy with Column Name(s)'))
        self.copyHeaderColumnsToClipboard = self.copySpecialMenu.addAction(self.tr('Copy Column Name(s)'))
        self.copyAsText = self.copySpecialMenu.addAction(self.tr('Copy As Text'))
        self.copyAsDelimited = self.copySpecialMenu.addAction(self.tr('Copy As Delimited'))
        self.copyAsJSON = self.copySpecialMenu.addAction(self.tr('Copy As JSON'))
        self.copyAsXML = self.copySpecialMenu.addAction(self.tr('Copy As XML'))
        self.copyAsHTML = self.copySpecialMenu.addAction(self.tr('Copy As HTML'))

        # copy to Python source code sub-submenu
        self.copyPythonAsText = self.copyToPythonMenu.addAction(self.tr('As Text'))
        self.copyPythonAsTuple = self.copyToPythonMenu.addAction(self.tr('As Tuple'))
        self.copyPythonAsList = self.copyToPythonMenu.addAction(self.tr('As List'))
        self.copyPythonAsDict = self.copyToPythonMenu.addAction(self.tr('As Dict'))

        self.editMenu.triggered.connect(self.editAction)

##        #copy to source code submenu
##        self.copyToSourceCodeMenu.addAction(QAction('C++', self)) ## acabar
##        self.copyToSourceCodeMenu.addAction(QAction('C#', self)) ## acabar
##        self.copyToSourceCodeMenu.addAction(QAction('Delphi', self)) ## acabar
##        self.copyToSourceCodeMenu.addAction(QAction('Java', self)) ## acabar
##        self.copyToSourceCodeMenu.addAction(QAction('Python', self)) ## acabar

##        # ideas
##        algo del estilo llamadas RESTFUL con datos del CSV...

    def addToolsMenu(self):
        """add TOOLS menu"""

        #explorer action
        self.explorer = QAction(QIcon(':images/explorer.png'), self.tr('Explorer'), self)
        self.explorer.setShortcut('Ctrl+E')
        self.explorer.setStatusTip(self.tr('Explorer'))
        self.explorer.triggered.connect(self.explorerToolAction)

        #search action
        self.search = QAction(QIcon(':images/search.png'), self.tr('Search'), self)
        self.search.setShortcut('Ctrl+F')
        self.search.setStatusTip(self.tr('Search'))
        self.search.triggered.connect(self.searchToolAction)

        #tools menu
        menubar = self.menuBar()
        toolsMenu = menubar.addMenu(self.tr('Tools'))
        toolsMenu.addAction(self.explorer)
        toolsMenu.addAction(self.search)

    def addConfigMenu(self):
        """add CONFIG menu"""

        #restore session action
        self.restoreSession = QAction(self.tr('Restore Session'), self)
        self.restoreSession.setCheckable(True)
        self.restoreSession.setChecked(config.config_restore)
        self.restoreSession.setStatusTip(self.tr('Restore Session'))
        self.restoreSession.changed.connect(self.restoreSessionConfigAction)

        #header row action
        self.headerRow = QAction(self.tr('Header Row'), self)
        self.headerRow.setCheckable(True)
        self.headerRow.setChecked(config.config_headerrow)
        self.headerRow.setStatusTip(self.tr('Header Row'))
        self.headerRow.changed.connect(self.headerRowConfigAction)

        #options action
        self.settings = QAction(QIcon(':images/options.png'), self.tr('Options...'), self)
        self.settings.setStatusTip(self.tr('Options'))
        self.settings.triggered.connect(self.optionsDialogAction)

        #config menu
        menubar = self.menuBar()
        configMenu = menubar.addMenu(self.tr('Config'))
        configMenu.addAction(self.restoreSession)
        configMenu.addAction(self.headerRow)
        configMenu.addSeparator()
        configMenu.addAction(self.settings)

    def addHelpMenu(self):
        """add HELP menu"""

        #update action
        self.update = QAction(QIcon(':images/update.png'), self.tr('Update CSV Tools'), self)
        self.update.setStatusTip(self.tr('Update CSV Tools'))
        #####self.about.triggered.connect(self.aboutDialogAction)

        #about action
        self.about = QAction(QIcon(':images/about.png'), self.tr('About'), self)
        self.about.setStatusTip(self.tr('About'))
        self.about.triggered.connect(self.aboutDialogAction)

        #help menu
        menubar = self.menuBar()
        helpMenu = menubar.addMenu(self.tr('Help'))
        helpMenu.addAction(self.update)
        helpMenu.addSeparator()
        helpMenu.addAction(self.about)

    def addMenus(self):
        """add menus to application"""

        self.addFileMenu()
        self.addEditMenu()
        self.addToolsMenu()
        self.addConfigMenu()
        self.addHelpMenu()
##        copy to GIS dataset
##        la idea es añadir formatos como por ejemplo GeoJson, Kml, etc...
##        seguramente habra que añadir un wizard preguntando p.ej q columna contiene
##        coordenada X, Y, etc...
##        pensar hasta que punto esto NO ES COPY sino es UN EXPORT.

    def addSplitter(self):
        """add splitter widget"""
        self.splitter = QSplitter(Qt.Horizontal)

    def addExplorer(self):
        """add explorer widget"""
        self.explorer = QExplorer('.')
        self.explorer.clickedFile.connect(self.explorerClickedFileEvent)

    def addSearch(self):
        """add search widget"""
        self.search = QSearch()
        self.search.searchClicked.connect(self.searchSearchClickedEvent)
        self.search.resultClicked.connect(self.searchResultClickedEvent)

    def addToolTab(self):
        self.toolTab = QTabWidget(self.splitter)
        #self.toolTab.setTabPosition(QTabWidget.South)
        index = self.toolTab.addTab(self.explorer, QIcon(':images/explorer.png'), 'Explorer')
        self.toolTab.setTabToolTip(index, 'Explorer')
        index = self.toolTab.addTab(self.search, QIcon(':images/search.png'), 'Search')
        self.toolTab.setTabToolTip(index, 'Search')

    def addTab(self):
        """add tab widget"""
        self.tab = QTabWidget(self.splitter)
        self.tab.setMovable(True)
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.tabCloseRequestedEvent)
        self.tab.currentChanged.connect(self.tabCurrentChangedEvent)
        self.splitter.setStretchFactor(1, 1)
        # set context tabbar menu event
        self.tab.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab.tabBar().customContextMenuRequested.connect(self.tabBarcustomContextMenuRequestedEvent)
        # set tab moved event
        self.tab.tabBar().tabMoved.connect(self.tabBartabMovedEvent)

    def addStatusBar(self):
        """add status bar widget"""
        self.statusBar = QStatus()
        self.statusBar.changedFontSize.connect(self.statusBarChangedFontSizeEvent)

    #
    # init
    #

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setWindowIcon(QIcon(':images/app.png'))
        self.setWindowTitle(self.tr("CSV Tools"))
        self.setAcceptDrops(True)
        self.resize(800, 400)

        # add widgets
        self.addMenus()
        self.addSplitter()
        self.addExplorer()
        self.addSearch()
        self.addToolTab()
        self.addTab()
        self.addStatusBar()

        # enable/disable diferent menu options
        self.tabCurrentChangedEvent()

        # central widget
        self.hbox = QVBoxLayout()
        self.hbox.addWidget(self.splitter, 1)
        self.hbox.addWidget(self.statusBar, -1)
        self.hbox.setContentsMargins(0, 4, 0, 0)
        centralWidget = QWidget()
        centralWidget.setLayout(self.hbox)
        self.setCentralWidget(centralWidget)

#
# MAIN
#


def main():
    app = QApplication(sys.argv)

    translator = QTranslator()
    translator.load("i18n/es_ES.qm")
    app.installTranslator(translator)

    main = MainWindow()
    main.show()

    app.removeTranslator(translator)

    if config.config_restore:
        main.restoreLastSession()

    sys.exit(app.exec_())


# http://rowinggolfer.blogspot.com.es/2010/05/qtreeview-and-qabractitemmodel-example.html
# https://wiki.python.org/moin/PyQt/Creating%20a%20context%20menu%20for%20a%20tree%20view
# http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py

# http://popdevelop.com/2010/05/an-example-on-how-to-make-qlabel-clickable/
# http://pyqt.sourceforge.net/Docs/PyQt4/classes.html
# print QtCore.QCoreApplication.translate("MyWindow", "About")
# https://kuanyui.github.io/2014/09/03/pyqt-i18n/
# http://pyqt.sourceforge.net/Docs/PyQt4/i18n.html
# The release manage may optionally use pyrcc4 to embed the .qm files, along with other application
# resources such as icons, in a Python module. This may make packaging and distribution of the application easier.
# http://stackoverflow.com/questions/13032774/pyqt-english-to-finnish-translation
# 		self._app.removeTranslator(self._enTranslator)
#		self._app.installTranslator(self._deTranslator)
#		self.retranslateUi(self)
# http://activityworkshop.net/software/beaver/pyqt.html
if __name__ == "__main__":
    main()
