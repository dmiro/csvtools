# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.about import QAbout
from widgets.preferences import Preferences
from widgets.report import QReport
from widgets.importwiz import QImportWiz
from widgets.csvm import QCsv
from widgets.explorer import QExplorer
from widgets.status import QStatus
from widgets.search import QSearch
from widgets.opencsvfiledialog import QOpenCsvFileDialog
from widgets.csvwiz import QCsvWiz
from widgets.helpers.qtabbardoubleclick import QTabBarDoubleClick
from lib.document import Document, Xsl, Csv, NewFilenameFactory
from lib.config import config
from lib.helper import waiting, get_excel_sheets, QStringToUnicode

import lib.images_rc
import sys
import os


class MainWindow(QMainWindow):

    #
    # private
    #

    def addCsvToTab(self, csvDoc):

        # add csv to tab
        csv = QCsv(csvDoc)
        csv.selectionChanged_.connect(self.csvSelectionChangedEvent)
        csv.fileChanged.connect(self.csvFileChangedEvent)
        filename = os.path.basename(csvDoc.filename)
        index = self.tab.addTab(csv, filename)
        self.tab.setCurrentIndex(index)

        # add file to recent files
        if not csv.document.isNew:
            self.addRecentFile(csv)
            self.refreshRecentFileActions()
            self.saveSessionFile()

    def reload(self, csv):
        @waiting
        def _reload():
            csv.document.load()
            self.addRecentFile(csv)
            self.refreshRecentFileActions()
            self.saveSessionFile()
            self.refreshStatusTab(csv)
        # confirm reload
        if csv.document.hasChanges():
            reloadMsg = self.tr('Are you sure you want to reload the current file and lose your changes?')
            reply = QMessageBox.question(self, self.tr('Message'), reloadMsg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        # csv wizard
        if config.wizard_showToReloadFile:
            document = QCsvWiz.getReloadFileName(csv.document, self)
            if document:
                csv.setDocument(document)
            else:
                return
        # reload
        _reload()

    @waiting
    def importExcel(self, filename, sheets):
        warnings = []
        for sheet in sheets:
            try:
                newFilename = NewFilenameFactory.getNewFilename()
                csvDoc = Csv(newFilename)
                csvDoc.importXsl(filename, sheet)
                self.addCsvToTab(csvDoc)
            except IOError:
                warnings.append('No such file {0}'.format(filename))
            except Exception, e:
                warnings.append('Error opening file {0}: {1}'.format(filename, e))
        if warnings:
            report = QReport(warnings)
            report.exec_()

    def openCsv(self, filenames):
        """open a csv file.
        This function accepts as single parameter: *path to a file*, *file path list*, *Document* or a *list of Document*
        The last two types usually come from a recent o session file.
        """
        if filenames:
            if isinstance(filenames, QString):
                filenames = str(filenames)
            if isinstance(filenames, basestring):
                filenames = [filenames]
            if isinstance(filenames, Document):
                filenames = [filenames]
            warnings = []
            for filename in filenames:
                try:

                    # if file exist
                    if isinstance(filename, Document):
                        file_ = str(filename.filename)
                    else:
                        file_ = filename
                    for index in range(self.tab.count()):
                        csv = self.tab.widget(index)
                        if file_ in csv.document.filename:
                            self.tab.setCurrentIndex(index)
                            return

                    # open
                    if isinstance(filename, Document):
                        filename.load()
                        self.addCsvToTab(filename)
                    else:
                        csvDoc = Csv(file_)
                        csvDoc.load()
                        self.addCsvToTab(csvDoc)

                except IOError:
                    if isinstance(filename, Document):
                        filename = filename.filename
                    warnings.append('No such file {0}'.format(filename))
                except Exception, e:
                    if isinstance(filename, Document):
                        filename = filename.filename
                    warnings.append('Error opening file {0}: {1}'.format(filename, e))
            if warnings:
                report = QReport(warnings)
                report.exec_()

    def newCsv(self):
        warnings = []
        try:
            newFilename = NewFilenameFactory.getNewFilename()
            csvDoc = Csv(newFilename)
            csvDoc.new()
            self.addCsvToTab(csvDoc)
        except Exception, e:
            warnings.append('Error : {0}'.format(e))
        if warnings:
            report = QReport(warnings)
            report.exec_()

    def saveFile(self, csv):
        if csv.document.isNew:
            # use csv wizard
            if config.wizard_showToSaveFile:
                document = QCsvWiz.getSaveNewFileName(csv.document, self)
                if document:
                    csv.setDocument(document)
                    return self.saveAsFile(csv)
            # save without wizard
            else:
                return self.saveAsFile(csv)
        else:
            # use csv wizard
            if config.wizard_showToSaveFile:
############ falta verificar q pasa si cambio csv y luego cancelo el wizard
                document = QCsvWiz.getSaveFileName(csv.document, self)
                if document:
                    document.save()
                    csv.setDocument(document)
############ hace falta cambiarlo, solo refresh csv no todo
                    self.addRecentFile(csv)
                    self.refreshRecentFileActions()
                    self.saveSessionFile()
                    self.refreshStatusTab(csv)
                    return True
            # save without wizard
            else:
                csv.document.save()
                self.refreshStatusTab(csv)
                return True
        return False

    def saveAsFile(self, csv):
        filename = QFileDialog.getSaveFileName(self, self.tr('Save as file'),
                                               csv.document.filename,
                                               "Csv Files (*.csv)")
        if filename:
            filename = str(filename)
            csv.document.save(filename)
            self.addRecentFile(csv)
            self.refreshRecentFileActions()
            self.saveSessionFile()
            self.refreshStatusTab(csv)
            return True
        else:
            return False

    def saveACopyAsFile(self, csv):
        filename = QFileDialog.getSaveFileName(self, self.tr('Save a copy as file'),
                                               csv.document.filename,
                                               "Csv Files (*.csv)")
        if filename:
            filename = str(filename)
            csv.document.saveACopy(filename)
            return True
        else:
            return False

    def saveAllFiles(self):
        for index in range(self.tab.count()):
            csv = self.tab.widget(index)
            if csv.document.hasChanges():
                self.saveFile(csv)

    def saveToExit(self):
        """
        """
        for index in range(self.tab.count()):
            csv = self.tab.widget(index)
            if csv:
                # before closing tab we need to check if save file
                if csv.document.hasChanges():
                    saveFileMsg = self.tr('Save file {0}?'.format(csv.document.filename))
                    reply = QMessageBox.question(self, self.tr('Save'), saveFileMsg, QMessageBox.Yes,
                                                 QMessageBox.No, QMessageBox.Cancel)
                    if reply == QMessageBox.Yes:
                        next = self.saveFile(csv)
                    elif reply == QMessageBox.Cancel:
                        next = False
                    else:
                        next = True
                    if not next:
                        return False
        return True

    def emptyRecentFiles(self):
        """empty recent files and refresh menu
        """
        config.file_recent = []
        self.refreshRecentFileActions()

    def restoreLastSession(self):
        """retrieve files the last session
        """
        fileSession = [Csv.fromJson(data) for data in config.file_session]
        self.openCsv(fileSession)

    def checkRecentFiles(self):
        """check recent files
        """
        fileRecentChecked = []
        fileRecent = [Csv.fromJson(data) for data in config.file_recent]
        for csv in fileRecent:
            if os.path.isfile(str(csv.filename)):
               fileRecentChecked.append(csv)
        config.file_recent = [mcsv.toJson() for mcsv in fileRecentChecked]

    def refreshRecentFileActions(self):
        """update recent files menu
        """
        self.recent.clear()
        fileRecent = [Csv.fromJson(data) for data in config.file_recent]
        for index, csv in enumerate(fileRecent):
            action = QAction("%d. %s" % (index + 1, csv.filename), self)
            action.setStatusTip("%s %s" % (self.tr('Open'), csv.filename))
            action.triggered[()].connect(lambda csv=csv: self.openCsv(csv))
            self.recent.addAction(action)
        self.recent.addSeparator()
        empty = QAction(self.tr('Empty'), self)
        empty.setStatusTip(self.tr('Empty recent list'))
        empty.triggered.connect(self.emptyRecentFiles)
        empty.setDisabled(len(config.file_recent) == 0)
        self.recent.addAction(empty)

    def addRecentFile(self, csv):
        """add in config file the last opened file
        """
        # convert from json to Csv
        file_recent = [Csv.fromJson(data) for data in config.file_recent]
        # add Csv to recent list
        if csv.document in file_recent:
            file_recent.remove(csv.document)
        file_recent.insert(0, csv.document)
        # convert from Csv to json
        config.file_recent = [mcsv.toJson() for mcsv in file_recent]

    def saveSessionFile(self):
        """save in config file the session files
        """
        config.file_session = [self.tab.widget(index).document.toJson()
                                for index in range(self.tab.count())
                                if (self.tab.widget(index).document.isNew == False)]

    def searchText(self, text, tabIndex, matchMode, matchCaseOption):
        csv = self.tab.widget(tabIndex)
        tabText = self.tab.tabText(tabIndex)
        tabToolTip = self.tab.tabToolTip(tabIndex)
        result = csv.search(text, matchMode, matchCaseOption)
        if len(result) > 0:
            return {'tabText':tabText, 'tabToolTip': tabToolTip, 'result':result}

    def refreshStatusTab(self, csv):
        if csv:
            index = self.tab.indexOf(csv)
            self.tab.setTabText(index, os.path.basename(csv.document.filename))
            self.tab.setTabToolTip(index, csv.document.filename)
            tabBar = self.tab.tabBar()
            if csv.hasChanges():
                tabBar.setTabTextColor(index, Qt.red)
            else:
                tabBar.setTabTextColor(index, Qt.black)
            currentCsv = self.tab.currentWidget()
            if csv == currentCsv:
                self.statusBar.setValues(csv.linesValue(), csv.columnsValue(), csv.sizeValue(),
                                         csv.encodingValue(), csv.modifiedValue(), csv.itemsValue(),
                                         csv.averageValue(), csv.countChanges(), csv.sumValue(), csv.pointSizeValue())
        else:
            self.statusBar.setValues(None, None, None, None, None, None, None, None, None, None)

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
                    # use csv wizard
                    if config.wizard_showToDropFile:
                        csv = QCsvWiz.getDropFileName(filename, self)
                        if csv:
                            self.openCsv(csv)
                    # open csv with standard parameters
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
            self.importExcel(filename, sheets)

    def importDialogAction(self):
        """import xls/xlsx dialog
        """
        filename = QFileDialog.getOpenFileName(self, self.tr('Import file'), '', "Excel Files (*.xlsx *.xls)")
        if filename:
            self.importExcelAction(filename)

    def newFileAction(self):
        """new csv
        """
        self.newCsv()

    def openDialogAction(self):
        """open csv dialog
        """
        filename, useWizard = QOpenCsvFileDialog.getOpenFileName(self)
        if filename:
            # use csv wizard
            if useWizard:
               csv = QCsvWiz.getOpenFileName(filename, self)
               if csv:
                    self.openCsv(csv)
            # open csv with standard parameters
            else:
                filename = str(filename)
                self.openCsv(filename)

    def exitAction(self):
        """exit action
        """
        self.close()

    def closeFileAction(self):
        """close current file
        """
        index = self.tab.currentIndex()
        if index > -1:
            self.tabCloseRequestedEvent(index)

    def closeAllFilesAction(self):
        """close all files
        """
        while self.tab.count() > 0:
            self.tabCloseRequestedEvent(0)

    def closeAllButThisFilesAction(self):
        """close all files except current file
        """
        thisCsv = self.tab.currentWidget()
        while self.tab.count() > 1:
            if self.tab.widget(0) != thisCsv:
                self.tabCloseRequestedEvent(0)
            else:
                self.tabCloseRequestedEvent(1)

    def reloadFileAction(self):
        """reload current file
        """
        csv = self.tab.currentWidget()
        if csv:
            self.reload(csv)

    def filePathToClipboardAction(self):
        """copy to clipboard current file path
        """
        csv = self.tab.currentWidget()
        if csv:
            clipboard = QApplication.clipboard()
            clipboard.setText(csv.document.filename)

    def allFilePathsToClipboardAction(self):
        """add all file path to clipboard
        """
        # retrieve path files
        files = []
        for index in range(self.tab.count()):
            csv = self.tab.widget(index)
            if not csv.document.isNew:
                files.append(csv.document.filename)
        # remove duplicates
        files = set(files)
        # copy path files to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(files))

    def saveFileAction(self):
        csv = self.tab.currentWidget()
        return self.saveFile(csv)

    def saveAsFileAction(self):
        csv = self.tab.currentWidget()
        return self.saveAsFile(csv)

    def saveACopyAsFileAction(self):
        csv = self.tab.currentWidget()
        return self.saveACopyAsFile(csv)

    def saveAllFilesAction(self):
        self.saveAllFiles()


    #
    # tool menu action methods
    #

    def _toolsAction(self, action):
        """show a tool widget
        """
        if action == self.explorerTool:
            self.toolTab.setCurrentIndex(0)
        if action == self.searchTool:
            self.toolTab.setCurrentIndex(1)
        self.dockToolTab.show()
        return

    #
    # config menu action methods
    #

    def preferencesDialogAction(self):
        """show precerences dialog
        """
        dialog = Preferences(self)
        dialog.exec_()
        # some preferences need updating widgets parameters
        self.tab.setMovable(not config.tabbar_lock)
        self.tab.setTabsClosable(config.tabbar_showclosebutton)
        self.tab.resize(1,1)
        csv = self.tab.currentWidget()
        if csv:
            csv.refresh()

    #
    # help menu action methods
    #

    def aboutDialogAction(self):
        """show about dialog
        """
        dialog = QAbout(self)
        dialog.exec_()

    #
    # event
    #

    def csvSelectionChangedEvent(self, csv):
        """ It occurs when selected or changed anything from csv file
        """
        self.refreshStatusTab(csv)

    def csvFileChangedEvent(self, csv):
        """ It occurs when csv file is modified outside the application
        """
        @waiting
        def _reload():
            self.tab.setCurrentWidget(csv)
            csv.document.load()
            self.refreshStatusTab(csv)

        hasChanges = csv.document.hasChanges()
        fileExist = os.path.isfile(csv.document.filename)

        if fileExist:
            if hasChanges:
                dialogMsg = '{0} This file has been modified by another program. Do you want to reload it and lose the changes made in csvtools?'.format(csv.document.filename)
            else:
                dialogMsg = '{0} This files has been modified by another program, Do you want to reload it?'.format(csv.document.filename)
            reply = QMessageBox.question(self, self.tr('Reload'), dialogMsg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                _reload()
        else:
            dialogMsg = '{0} doesn''t exist anymore. Keep this file in editor?'.format(csv.document.filename)
            reply = QMessageBox.question(self, self.tr('Close'), dialogMsg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                csv.deleteLater()           # Schedules this object for deletion.
                                            # It's very important to release your resources.
                index = self.tab.indexOf(csv)
                self.tab.removeTab(index)
                self.saveSessionFile()

    def statusBarChangedFontSizeEvent(self, fontSize):
        csv = self.tab.currentWidget()
        csv.setPointSize(fontSize)

    def tabCloseRequestedEvent(self, index):
        """event when a tab is closed: remove tab & update config
        """
        csv = self.tab.widget(index)
        if csv:
            # before closing tab we need to check if save file
            if csv.document.hasChanges():
                saveFileMsg = self.tr('Save file {0}?'.format(csv.document.filename))
                reply = QMessageBox.question(self, self.tr('Save'), saveFileMsg, QMessageBox.Yes,
                                             QMessageBox.No, QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    closeTab = self.saveFile(csv)
                elif reply == QMessageBox.No:
                    closeTab = True
                if reply == QMessageBox.Cancel:
                    closeTab = False
            else:
                closeTab = True
            # close tab
            if closeTab:
                csv.deleteLater()           # Schedules this object for deletion.
                                            # It's very important to release your resources.
                self.tab.removeTab(index)
                self.saveSessionFile()

    def tabCurrentChangedEvent(self, index=0):
        """event when a selected tab is changed
        """
        csv = self.tab.currentWidget()
        if csv:
            menubar = self.menuBar()
            editMenuAction = self.editMenu.menuAction()
            viewMenuAction = self.viewMenu.menuAction()
            toolsMenuAction = self.toolsMenu.menuAction()
            try:
                menubar.removeAction(editMenuAction)
                menubar.removeAction(viewMenuAction)
            except: pass
            self.editMenu = csv.editMenu()
            menubar.insertMenu(toolsMenuAction, self.editMenu)
            self.viewMenu = csv.viewMenu()
            menubar.insertMenu(toolsMenuAction, self.viewMenu)
            self.closeAllButThisOption.setDisabled(False)
            self.closeAllFilesOption.setDisabled(False)
            self.closeFileOption.setDisabled(False)
            self.filePathToClipboardOption.setDisabled(csv.document.isNew)
            self.allFilePathsToClipboardOption.setDisabled(False)
            self.saveFileOption.setDisabled(False)
            self.saveAllFilesOption.setDisabled(False)
            self.saveCopyFileOption.setDisabled(False)
            self.saveAsFileOption.setDisabled(False)
            self.reloadFileOption.setDisabled(csv.document.isNew)
            # refresh status bar
            self.refreshStatusTab(csv)
        else:
            try:
                self.editMenu.clear()
                self.editMenu.menuAction().setEnabled(False)
                self.viewMenu.clear()
                self.viewMenu.menuAction().setEnabled(False)
            except: pass
            self.closeAllButThisOption.setDisabled(True)
            self.closeAllFilesOption.setDisabled(True)
            self.closeFileOption.setDisabled(True)
            self.filePathToClipboardOption.setDisabled(True)
            self.allFilePathsToClipboardOption.setDisabled(True)
            self.saveFileOption.setDisabled(True)
            self.saveAllFilesOption.setDisabled(True)
            self.saveCopyFileOption.setDisabled(True)
            self.saveAsFileOption.setDisabled(True)
            self.reloadFileOption.setDisabled(True)
            # refresh status bar
            self.refreshStatusTab(None)

    def tabBarcustomContextMenuRequestedEvent(self, point):
        tab = self.tab.tabBar()
        # set current tab index
        tabIndex = tab.tabAt(point)
        if self.tab.currentIndex() != tabIndex:
            self.tab.setCurrentIndex(tabIndex)
        # make and show menu
        menu = QMenu("Tab Menu")
        menu.addAction(self.saveFileOption)
        menu.addAction(self.saveAsFileOption)
        menu.addAction(self.reloadFileOption)
        menu.addAction(self.closeFileOption)
        menu.addAction(self.closeAllFilesOption)
        menu.addAction(self.closeAllButThisOption)
        menu.addSeparator()
        menu.addAction(self.filePathToClipboardOption)
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
            csv = self.tab.widget(index)
            if file_ in csv.document.filename:
                self.tab.setCurrentIndex(index)
                csv.setSelectCell(row, column)

    def explorerClickedFileEvent(self, filename):
        filename = str(filename)
        _, fileExtension = os.path.splitext(filename)
        if fileExtension == '.xls' or fileExtension == '.xlsx':
            self.importExcelAction(filename)
        else:
            self.openCsv(filename)

    def closeEvent (self, event):
        exit = self.saveToExit()
        if exit:
            event.accept()
        else:
            event.ignore()

    #
    # widgets
    #

    def addFileMenu(self):
        """add FILE menu
        """
        # new file action
        self.newFileOption = QAction(QIcon(':images/new.png'), self.tr('&New'), self)
        self.newFileOption.setShortcut(QKeySequence.New)
        self.newFileOption.setStatusTip(self.tr('New Csv file'))
        self.newFileOption.triggered.connect(self.newFileAction)

        # open file action
        self.openFileOption = QAction(QIcon(':images/open.png'), self.tr('&Open'), self)
        self.openFileOption.setShortcut(QKeySequence.Open)
        self.openFileOption.setStatusTip(self.tr('Open Csv file'))
        self.openFileOption.triggered.connect(self.openDialogAction)

        # import file action
        self.importFileOption = QAction(QIcon(':images/import.png'), self.tr('Import'), self)
        self.importFileOption.setShortcut('Ctrl+I')
        self.importFileOption.setStatusTip(self.tr('Import Excel file'))
        self.importFileOption.triggered.connect(self.importDialogAction)

        # reload file action
        self.reloadFileOption = QAction(QIcon(':images/reload.png'), self.tr('Reload from Disk'), self)
        self.reloadFileOption.setShortcut('Ctrl+R')
        self.reloadFileOption.setStatusTip(self.tr('Reload file from disk'))
        self.reloadFileOption.triggered.connect(self.reloadFileAction)

        # Save
        self.saveFileOption = QAction(QIcon(':images/save.png'), self.tr('Save'), self)
        self.saveFileOption.setShortcut('Ctrl+S')
        self.saveFileOption.setStatusTip(self.tr('Save file'))
        self.saveFileOption.triggered.connect(self.saveFileAction)

        # Save As..
        self.saveAsFileOption = QAction(self.tr('Save As..'), self)
        self.saveAsFileOption.setShortcut('Ctrl+Alt+S')
        self.saveAsFileOption.setStatusTip(self.tr('Save file as..'))
        self.saveAsFileOption.triggered.connect(self.saveAsFileAction)

        # Save a Copy As..
        self.saveCopyFileOption = QAction(self.tr('Save a Copy As..'), self)
        self.saveCopyFileOption.setStatusTip(self.tr('Save a copy file as..'))
        self.saveCopyFileOption.triggered.connect(self.saveACopyAsFileAction)

        # Save All
        self.saveAllFilesOption = QAction(self.tr('Save All'), self)
        self.saveAllFilesOption.setShortcut('Ctrl+Shift+S')
        self.saveAllFilesOption.setStatusTip(self.tr('Save all files'))
        self.saveAllFilesOption.triggered.connect(self.saveAllFilesAction)

        # close file action
        self.closeFileOption = QAction(QIcon(':images/close.png'), self.tr('Close'), self)
        self.closeFileOption.setShortcut(QKeySequence.Close)
        self.closeFileOption.setStatusTip(self.tr('Close file'))
        self.closeFileOption.triggered.connect(self.closeFileAction)

        # close all files action
        self.closeAllFilesOption = QAction(self.tr('Close All'), self)
        self.closeAllFilesOption.setStatusTip(self.tr('Close all files'))
        self.closeAllFilesOption.triggered.connect(self.closeAllFilesAction)

        # Close All BUT This action
        self.closeAllButThisOption = QAction(self.tr('Close All BUT This'), self)
        self.closeAllButThisOption.setStatusTip(self.tr('Close all except the file currently being edited'))
        self.closeAllButThisOption.triggered.connect(self.closeAllButThisFilesAction)

        # File Path to Clipboard action
        self.filePathToClipboardOption = QAction(self.tr('File Path to Clipboard'), self)
        self.filePathToClipboardOption.setStatusTip(self.tr('Copy file path to clipboard'))
        self.filePathToClipboardOption.triggered.connect(self.filePathToClipboardAction)

        # File Path to Clipboard action
        self.allFilePathsToClipboardOption = QAction(self.tr('All File Paths to Clipboard'), self)
        self.allFilePathsToClipboardOption.setStatusTip(self.tr('Copy all file paths to clipboard'))
        self.allFilePathsToClipboardOption.triggered.connect(self.allFilePathsToClipboardAction)

        # exit action
        self.exitApp = QAction(QIcon(':images/exit.png'), self.tr('E&xit'), self)
        self.exitApp.setShortcut(QKeySequence.Quit)
        self.exitApp.setStatusTip(self.tr('Exit to Csvtools'))
        self.exitApp.triggered.connect(self.exitAction)

        # file menu
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu(self.tr('&File'))
        self.fileMenu.addAction(self.newFileOption)
        self.fileMenu.addAction(self.openFileOption)
        self.fileMenu.addAction(self.importFileOption)
        self.fileMenu.addAction(self.reloadFileOption)
        self.fileMenu.addAction(self.saveFileOption)
        self.fileMenu.addAction(self.saveAsFileOption)
        self.fileMenu.addAction(self.saveCopyFileOption)
        self.fileMenu.addAction(self.saveAllFilesOption)
        self.fileMenu.addAction(self.closeFileOption)
        self.fileMenu.addAction(self.closeAllFilesOption)
        self.fileMenu.addAction(self.closeAllButThisOption)
        self.recent = self.fileMenu.addMenu(self.tr('Recent Files'))
        self.refreshRecentFileActions()
        self.fileMenu.addSeparator()
        self.copyToClipboardMenu = self.fileMenu.addMenu(self.tr('Copy to Clipboard'))
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitApp)

        # clipboard submenu
        self.copyToClipboardMenu.addAction(self.filePathToClipboardOption)
        self.copyToClipboardMenu.addAction(self.allFilePathsToClipboardOption)

    def addEditMenu(self):
        """add EDIT menu
        """
        # edit menu
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu(self.tr('Edit'))
        self.editMenu.menuAction().setEnabled(False)

    def addViewMenu(self):
        """add VIEW menu
        """
        #view menu
        menubar = self.menuBar()
        self.viewMenu = menubar.addMenu(self.tr('View'))
        self.viewMenu.menuAction().setEnabled(False)

    def addToolsMenu(self):
        """add TOOLS menu
        """
        # tools menu
        menubar = self.menuBar()
        self.toolsMenu = menubar.addMenu(self.tr('Tools'))

        # explorer action
        self.explorerTool = self.toolsMenu.addAction(QIcon(':images/explorer.png'), self.tr('Explorer'))
        self.explorerTool.setShortcut('Ctrl+E')
        self.explorerTool.setStatusTip(self.tr('Explorer'))

        # search action
        self.searchTool = self.toolsMenu.addAction(QIcon(':images/search.png'), self.tr('Search'))
        self.searchTool.setShortcut('Ctrl+F')
        self.searchTool.setStatusTip(self.tr('Search'))

        # connect tools action
        self.toolsMenu.triggered.connect(self._toolsAction)

    def addSettingsMenu(self):
        """add SETTINGS menu
        """
        # config menu
        menubar = self.menuBar()
        self.settingsMenu = menubar.addMenu(self.tr('Settings'))

        # options action
        self.preferences = self.settingsMenu.addAction(QIcon(':images/options.png'), self.tr('Preferences...'))
        self.preferences.setStatusTip(self.tr('General preferences'))
        self.preferences.triggered.connect(self.preferencesDialogAction)

    def addHelpMenu(self):
        """add HELP menu
        """
        # update action
        self.update = QAction(QIcon(':images/update.png'), self.tr('Update CSV Tools'), self)
        self.update.setStatusTip(self.tr('Check for new version'))
        #####self.about.triggered.connect(self.updateCsvgAction)

        # about action
        self.about = QAction(QIcon(':images/about.png'), self.tr('About'), self)
        self.about.setStatusTip(self.tr('About this application'))
        self.about.triggered.connect(self.aboutDialogAction)

        # help menu
        menubar = self.menuBar()
        helpMenu = menubar.addMenu(self.tr('Help'))
        helpMenu.addAction(self.update)
        helpMenu.addSeparator()
        helpMenu.addAction(self.about)

    def createMenus(self):
        """add menus to application
        """
        self.addFileMenu()
        self.addEditMenu()
        self.addViewMenu()
        self.addToolsMenu()
        self.addSettingsMenu()
        self.addHelpMenu()
##        copy to GIS dataset
##        la idea es añadir formatos como por ejemplo GeoJson, Kml, etc...
##        seguramente habra que añadir un wizard preguntando p.ej q columna contiene
##        coordenada X, Y, etc...
##        pensar hasta que punto esto NO ES COPY sino es UN EXPORT.

    def createToolTab(self):
        """create search and explorer tools and adds in toolbar
        """
        # explorer widget
        self.explorer = QExplorer('.')
        self.explorer.clickedFile.connect(self.explorerClickedFileEvent)
        # search widget
        self.search = QSearch()
        self.search.searchClicked.connect(self.searchSearchClickedEvent)
        self.search.resultClicked.connect(self.searchResultClickedEvent)
        # toolbar
        self.toolTab = QTabWidget()
        index = self.toolTab.addTab(self.explorer, QIcon(':images/explorer.png'), 'Explorer')
        self.toolTab.setTabToolTip(index, 'Explorer')
        index = self.toolTab.addTab(self.search, QIcon(':images/search.png'), 'Search')
        self.toolTab.setTabToolTip(index, 'Search')

    def tabBarDoubleClickEvent(self, index):
        if config.tabbar_doubleclicktoclose and index > -1:
            self.tabCloseRequestedEvent(index)

    def createCsvTab(self):
        """add tab widget for csv widgets
        """
        self.tab = QTabWidget()
        self.tab.setTabBar(QTabBarDoubleClick())
        self.tab.setMovable(not config.tabbar_lock)
        self.tab.setTabsClosable(config.tabbar_showclosebutton)
        self.tab.tabCloseRequested.connect(self.tabCloseRequestedEvent)
        self.tab.currentChanged.connect(self.tabCurrentChangedEvent)
        # set context tabbar menu event
        self.tab.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab.tabBar().customContextMenuRequested.connect(self.tabBarcustomContextMenuRequestedEvent)
        self.tab.tabBar().doubleClick.connect(self.tabBarDoubleClickEvent)
        # set tab moved event
        self.tab.tabBar().tabMoved.connect(self.tabBartabMovedEvent)

    def createStatusBar(self):
        """add status bar widget
        """
        self.statusBar = QStatus()
        self.statusBar.changedFontSize.connect(self.statusBarChangedFontSizeEvent)

    #
    # init
    #

    def __init__(self, *args):

        # init
        super(MainWindow, self).__init__(*args)
        self.setWindowIcon(QIcon(':images/app.png'))
        self.setWindowTitle(self.tr("CSV Tools"))
        self.setAcceptDrops(True)
        self.resize(800, 400)

        # check recent files
        if config.recentfiles_check:
            self.checkRecentFiles()

        # add widgets
        self.createMenus()
        self.createToolTab()
        self.createCsvTab()
        self.createStatusBar()

        # enable/disable diferent menu options
        self.tabCurrentChangedEvent()

        # central widget
        self.setCentralWidget(self.tab)

        # statusbar
        self.setStatusBar(self.statusBar)

        # dock widget
        self.dockToolTab = QDockWidget("Tools", self)
        self.dockToolTab.setWidget(self.toolTab)
        if config.view_positiontools == 1:
            self.addDockWidget(Qt.RightDockWidgetArea, self.dockToolTab)
        elif config.view_positiontools == 2:
            self.addDockWidget(Qt.TopDockWidgetArea, self.dockToolTab)
        elif config.view_positiontools == 3:
            self.addDockWidget(Qt.BottomDockWidgetArea, self.dockToolTab)
        else:
            self.addDockWidget(Qt.LeftDockWidgetArea, self.dockToolTab)
        if not config.view_showtools:
            self.dockToolTab.hide()


#
# MAIN
#

def main():

    # taskbar icon in Windows 7 (http://stackoverflow.com/a/1552105/2270217)
    import ctypes
    myappid = '3engine.csvtools.1000'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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
