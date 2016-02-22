from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qcomboboxenter import QComboBoxEnter
from favfolders import QFavFolders
from lib.config import config
import lib.images_rc
import sys
import os


class QExplorer(QWidget):

    #
    # public
    #
    
    clickedFile = pyqtSignal(str)

    def setRootPath(self, rootPath):
        index = self.modelDirs.index(rootPath)
        if not index.isValid():
            index = self.modelDirs.index('.')
        self._modelFilesClickedEvent(index)

    #
    # private
    #

    def _loadFavoriteFolderConfig(self):
        self.favoriteFolderMenu.clear()
        for favFolder in config.favFolders:
            nameFolder = favFolder[0]
            pathFolder = favFolder[1]
            action = QAction(nameFolder, self)
            action.setStatusTip(pathFolder)
            action.triggered[()].connect(lambda pathFolder=pathFolder: self.setRootPath(pathFolder))
            self.favoriteFolderMenu.addAction(action)
           
    def _loadConfig(self):
        # filter files widget
        self.filterFiles.addItems(config.filterFiles)
        # favorite folders widget
        self._loadFavoriteFolderConfig()
        # show unmatched disabled
        self.showUnmatchedDisabled.setChecked(config.showUnmatchedDisabled)
        # show column size
        self.showColumnSize.setChecked(config.showColumnSize)
        # show columns date modified 
        self.showColumnDateModified.setChecked(config.showColumnDateModified)
        # show Column Size & show Column Date Modified
        self._setFileColumns()

    def _saveConfig(self):
        # filter files widget. Not add the first two filters 
        items = [str(self.filterFiles.itemText(i)) for i in range(self.filterFiles.count())]
        config.filterFiles = items[4:]
        # show unmatched disabled
        config.showUnmatchedDisabled = self.showUnmatchedDisabled.isChecked()
        # show column size
        config.showColumnSize = self.showColumnSize.isChecked()
        # show columns date modified 
        config.showColumnDateModified = self.showColumnDateModified.isChecked()

    def _getModelFiles(self, filter_):        
        modelFiles= QFileSystemModel()
        modelFiles.setRootPath('*')
        modelFiles.setFilter(QDir.AllDirs | QDir.Dirs | QDir.Files | QDir.NoDot)    # you set should always include the QDir.AllDirs enum value, otherwise
                                                                                    # QFileSystemModel won't be able to read the directory structure
                                                                                    # http://stackoverflow.com/a/9590345/2270217
        if isinstance(filter_, basestring):
            filter_ = [filter_]
        modelFiles.setNameFilters(filter_)
        nameFilterDisables = self.showUnmatchedDisabled.isChecked()
        modelFiles.setNameFilterDisables(nameFilterDisables)
        return modelFiles

    def _setFileColumns(self):
        self.treeFiles.setColumnHidden(1, not self.showColumnSize.isChecked())
        self.treeFiles.setColumnHidden(3, not self.showColumnDateModified.isChecked())
        self.treeFiles.resizeColumnToContents(1)
        self.treeFiles.resizeColumnToContents(2)
        self.treeFiles.resizeColumnToContents(3)
        self._saveConfig()
    
    #
    # event
    #

    def _modelFilesDoubleClickedEvent(self, index):
        fileInfo = self.modelFiles.fileInfo(index)
        isFile = fileInfo.isFile()
        if isFile:
            filePath = self.modelFiles.filePath(index)
            self.clickedFile.emit(filePath)
        
    def _modelFilesClickedEvent(self, index):        
        fileInfo = self.modelFiles.fileInfo(index)
        isDir = fileInfo.isDir()
        if isDir:          
            # update tree dirs
            filePath = self.modelFiles.filePath(index)
            self.treeDirs.setCurrentIndex(self.modelDirs.index(filePath))       
            # update tree files
            treeIndex = self.treeDirs.currentIndex()
            self._modelDirsClickedEvent(treeIndex)

    def _modelDirsClickedEvent(self, index):        
        # get filter to apply
        if self.filterFiles.currentIndex() == 0:
            filter_ = '*.csv'
        elif self.filterFiles.currentIndex() == 1:
            filter_ = ['*.xls','*.xlsx']
        elif self.filterFiles.currentIndex() == 2:
            filter_ = ['*.*']
        else:
            filter_ = str(self.filterFiles.currentText())
        # apply filter
        filePath = self.modelDirs.filePath(index)
        self.modelFiles = self._getModelFiles(filter_)
        self.treeFiles.setModel(self.modelFiles)
        self.treeFiles.setRootIndex(self.modelFiles.index(filePath))
    
    def _filterFilesClickedEvent(self):
        treeIndex = self.treeDirs.currentIndex()
        self._modelDirsClickedEvent(treeIndex)
        self._saveConfig()

    def _filterFilesCurrentIndexChangedEvent(self, currentIndex):
        self._filterFilesClickedEvent()

    def _menuOptionClickedEvent(self):
        heightWidget = self.optionsButton.height()
        point = self.optionsButton.mapToGlobal(QPoint(0, heightWidget))
        self.filterOptionsMenu.exec_(point)

    def _favoriteFolderButtonClickedEvent(self):
        favFolders = QFavFolders(self)
        if favFolders.exec_() == QDialog.Accepted:
            self._loadFavoriteFolderConfig()        
        
    def _toolBarFilesActionTriggeredEvent(self, action):
        # toolbar file actions
        if action == self.refreshFiles:
            self._filterFilesClickedEvent()
        # actions associate to options menu
        elif action == self.showUnmatchedDisabled:
            self._filterFilesClickedEvent()
        elif action == self.showColumnSize or action == self.showColumnDateModified:
            self._setFileColumns()
  
    def _toolBarDirsActionTriggeredEvent(self, action):
        if action == self.refreshDirs:
            self._filterFilesClickedEvent()
        elif action == self.userFolderDir:
            home = os.path.expanduser('~')
            # home = os.getenv('USERPROFILE') or os.getenv('HOME')
            if home:
                self.setRootPath(home)
        elif action == self.addFolderDir:
            pass #acabar

    def _treeDirscustomContextMenuRequestedEvent(self, point):
        # show menu
        globalPoint = self.treeDirs.mapToGlobal(point)
        self.menuDirsFiles.exec_(globalPoint)

    def _addFavoriteFolderAction(self):
        index = self.treeDirs.currentIndex()
        pathFolder = self.modelDirs.filePath(index)
        if pathFolder:
            pathFolder = str(pathFolder)
            nameFolder = os.path.basename(pathFolder)
            nameFolder, ok = QInputDialog.getText(self, self.tr('Add Favorite'), self.tr('Enter favorite name:'), text=nameFolder)
            if ok and nameFolder:
                # recuperar
                favFolders = config.favFolders
                favFolders.append([str(nameFolder), pathFolder])
                # salvar
                config.favFolders = favFolders
                # refresh favorites
                self._loadFavoriteFolderConfig()
    #
    # widget
    #

    def _addMenuDirsFiles(self):
        # action 
        self.addFavoriteFolder = QAction(QIcon(':images/favfolder.png'), self.tr('Add to Favorite Folder'), self,
                                         triggered=self._addFavoriteFolderAction)

        # menu
        self.menuDirsFiles = QMenu("TreeView Menu")
        self.menuDirsFiles.addAction(self.addFavoriteFolder)

    def _addToolBarDirsFiles(self):
        # action 
        self.refreshDirs = QAction(QIcon(':images/refresh.png'), self.tr('Refresh'), self)
        self.userFolderDir = QAction(QIcon(':images/home.png'), self.tr('User Folder'), self)
        self.addFolderDir = QAction(QIcon(':images/addfolder.png'), self.tr('Add Folder'), self)
        
        # favorite folder Menu
        self.favoriteFolderMenu = QMenu()

        # favorite folder ToolButton
        self.favoriteFolderButton = QToolButton()
        self.favoriteFolderButton.setMenu(self.favoriteFolderMenu)
        self.favoriteFolderButton.setIcon(QIcon(':images/favfolder.png'))
        self.favoriteFolderButton.setStatusTip(self.tr('Edit Favorite Folders'))
        self.favoriteFolderButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.favoriteFolderButton.clicked.connect(self._favoriteFolderButtonClickedEvent)

        # toolbar tree dir widget
        self.toolBarDirs= QToolBar()
        self.toolBarDirs.setIconSize(QSize(16, 16))
        self.toolBarDirs.addWidget(self.favoriteFolderButton)
        self.toolBarDirs.addSeparator()
        self.toolBarDirs.addAction(self.userFolderDir)
        self.toolBarDirs.addAction(self.addFolderDir)
        self.toolBarDirs.addSeparator()
        self.toolBarDirs.addAction(self.refreshDirs)        
        self.toolBarDirs.actionTriggered.connect(self._toolBarDirsActionTriggeredEvent)

    def _addToolBarTreeFiles(self):
        # actions
        self.showUnmatchedDisabled = QAction(self.tr('Show unmatched disabled'), self)
        self.showUnmatchedDisabled.setCheckable(True)
        self.showColumnSize = QAction('Show column Size', self)
        self.showColumnSize.setCheckable(True)
        self.showColumnDateModified = QAction(self.tr('Show column Date Modified'), self)
        self.showColumnDateModified.setCheckable(True)
        self.refreshFiles = QAction(QIcon(':images/refresh.png'), self.tr('Refresh'), self)
        
        # filter ComboBox
        self.filterFiles = QComboBoxEnter()        
        self.filterFiles.addItem(QIcon(':images/app.png'), 'Csv Files (*.csv)')
        self.filterFiles.addItem(QIcon(':images/app.png'), 'Excel Files (*.xlsx *.xls)')
        self.filterFiles.addItem(QIcon(':images/app.png'), 'All Files (*.*)')
        self.filterFiles.insertSeparator(3)
        self.filterFiles.setEditable(True)
        self.filterFiles.setAutoCompletion(True)
        self.filterFiles.setToolTip(self.tr('Filter Files'))
        self.filterFiles.setInsertPolicy(QComboBox.InsertAtBottom)
        self.filterFiles.setDuplicatesEnabled(False)
        self.filterFiles.enter.connect(self._filterFilesClickedEvent)
        self.filterFiles.currentIndexChanged.connect(self._filterFilesCurrentIndexChangedEvent)
        self.filterFiles.setCurrentIndex(0)
        self.filterFiles.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)

        # filter Menu
        self.filterOptionsMenu = QMenu()
        self.filterOptionsMenu.addAction(self.showUnmatchedDisabled)
        self.filterOptionsMenu.addAction(self.showColumnSize)
        self.filterOptionsMenu.addAction(self.showColumnDateModified)
        self.filterOptionsMenu.triggered.connect(self._toolBarFilesActionTriggeredEvent) 

        # filter options ToolButton
        self.optionsButton = QToolButton()
        self.optionsButton.setMenu(self.filterOptionsMenu)
        self.optionsButton.setIcon(QIcon(':images/filteroptions.png'))
        self.optionsButton.setStatusTip(self.tr('Filter Options'))
        self.optionsButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.optionsButton.clicked.connect(self._menuOptionClickedEvent)
        
        # tree files ToolBar
        self.toolBarFiles= QToolBar()
        self.toolBarFiles.setIconSize(QSize(16, 16))      
        self.toolBarFiles.addWidget(self.filterFiles)
        self.toolBarFiles.addWidget(self.optionsButton)      
        self.toolBarFiles.addSeparator()
        self.toolBarFiles.addAction(self.refreshFiles)  
        self.toolBarFiles.actionTriggered.connect(self._toolBarFilesActionTriggeredEvent) 

    def _addTreeViewDirsFiles(self):
        # model
        self.modelDirs= QFileSystemModel()
        self.modelDirs.setRootPath('*')
        self.modelDirs.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
          
        # TreeView
        self.treeDirs= QTreeView()
        self.treeDirs.setModel(self.modelDirs)
        self.treeDirs.setColumnHidden(1, True)
        self.treeDirs.setColumnHidden(2, True)
        self.treeDirs.setColumnHidden(3, True)
        self.treeDirs.setHeaderHidden(True)
        self.treeDirs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeDirslayout= QVBoxLayout()
        self.treeDirslayout.addWidget(self.toolBarDirs)
        self.treeDirslayout.addWidget(self.treeDirs)
        self.treeDirslayout.setContentsMargins(0, 0, 0, 0)
        self.treeDirsWidget = QWidget(self.splitter)
        self.treeDirsWidget.setLayout(self.treeDirslayout)
   
        # TreeView Signals
        self.treeDirs.clicked.connect(self._modelDirsClickedEvent)
        self.treeDirs.customContextMenuRequested.connect(self._treeDirscustomContextMenuRequestedEvent)

    def _addTreeViewTreeFiles(self):
        # model
        self.modelFiles = self._getModelFiles('*.*')
        
        # TreeView
        self.treeFiles= QTreeView()
        self.treeFiles.setModel(self.modelFiles)
        self.treeFiles.setItemsExpandable(False)
        self.treeFiles.setExpandsOnDoubleClick(False)
        self.treeFiles.setColumnHidden(2, True)
        self.treeFiles.setRootIsDecorated(False)
        self.treeFileslayout= QVBoxLayout()
        self.treeFileslayout.addWidget(self.toolBarFiles)
        self.treeFileslayout.addWidget(self.treeFiles)
        self.treeFileslayout.setContentsMargins(0, 0, 0, 0)
        self.treeFilesWidget = QWidget(self.splitter)
        self.treeFilesWidget.setLayout(self.treeFileslayout)

        # TreeView Signals
        self.treeFiles.clicked.connect(self._modelFilesClickedEvent)
        self.treeFiles.doubleClicked.connect(self._modelFilesDoubleClickedEvent)
        
    #
    # init
    #
        
    def __init__(self, rootPath, *args):
        QWidget.__init__(self, *args)

        # add Splitter
        self.splitter= QSplitter(Qt.Vertical)

        # add DIRS ToolBar
        self._addToolBarDirsFiles()
        
        # add DIRS TreeView
        self._addTreeViewDirsFiles()

        # add DIRS Context Menu
        self._addMenuDirsFiles()
        
        # add FILES ToolBar
        self._addToolBarTreeFiles()

        # add FILES TreeView        
        self._addTreeViewTreeFiles()

        # load config
        self._loadConfig()

        # main layout
        layout= QVBoxLayout()
        layout.addWidget(self.splitter)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)        
        self.setRootPath(rootPath)
