# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.config import config
import lib.images_rc
import os
import sys

class QFavFolders(QDialog):

    #
    # private
    #

    def _loadConfig(self):
        # favorite folders
        self.favFolders = config.favFolders

    def _saveConfig(self):
        # favorite folders
        model = self.favFoldersView.model()
        data = [[str(model.item(index, 0).text()), str(model.item(index, 1).text())]
                for index in range(model.rowCount())]
        config.favFolders = data

    def _addFavFolderToModel(self, model, nameFolder, pathFolder):
        index = model.rowCount()
        # name column
        item = QStandardItem(nameFolder)
        item.setEditable (False)          
        model.setItem (index, 0, item)
        # path folder column
        item = QStandardItem(pathFolder)
        item.setEditable (False)
        model.setItem (index, 1, item)  
        
    def _getFavFoldersList(self, favFolders):
        model = QStandardItemModel(0, 2)
        model.setHeaderData(0, Qt.Horizontal, self.tr('Name'))
        model.setHeaderData(1, Qt.Horizontal, self.tr('Path Folder'))
        for value in favFolders:
            # add row to model
            nameFolder = value[0]
            pathFolder = value[1]            
            self._addFavFolderToModel(model, nameFolder, pathFolder)          
        return model

    #
    # event
    #

    def _acceptButtonAcceptedEvent(self):
        self._saveConfig()
        self.accept()
        
    def _verticalButtonBoxClickedEvent(self, button):
        # add button
        if button == self.addButton:
            pathFolder = str(QFileDialog.getExistingDirectory(self, self.tr('Select Folder')))
            if pathFolder:
                nameFolder = os.path.basename(pathFolder)
                nameFolder, ok = QInputDialog.getText(self, self.tr('Add Favorite'), self.tr('Enter favorite name:'), text=nameFolder)
                if ok and nameFolder:
                    model = self.favFoldersView.model()
                    self._addFavFolderToModel(model, nameFolder, pathFolder)
                    self.acceptButton.setEnabled(True)

        # remove button
        elif button == self.removeButton:
            treeIndex = self.favFoldersView.currentIndex()
            if treeIndex:
               if treeIndex.isValid():
                   model = self.favFoldersView.model()
                   if model:
                       row = treeIndex.row()
                       model.removeRow(row)
                       self._treeViewclickedEvent()
                       self.acceptButton.setEnabled(True)
        
    def _treeViewclickedEvent(self):
        treeIndex = self.favFoldersView.currentIndex()
        if treeIndex:
            self.removeButton.setEnabled(treeIndex.isValid())
        else:
            self.removeButton.setEnabled(False)

    #
    # init
    #
        
    def __init__(self, *args):
        QDialog.__init__ (self, *args)

        # tree view
        self._loadConfig()
        model = self._getFavFoldersList(self.favFolders)
        self.favFoldersView = QTreeView()
        self.favFoldersView.setModel(model)
        self.favFoldersView.setRootIsDecorated(False)
        self.favFoldersView.clicked.connect(self._treeViewclickedEvent)

        # add & remove buttonbox
        self.addButton = QPushButton(self.tr('Add Favorite'), self)
        self.addButton.setIcon(QIcon(':images/favfolder.png'))
        self.removeButton = QPushButton(self.tr('Remove Favorite'), self)
        self.removeButton.setIcon(QIcon(':images/removefavfolder.png'))
        verticalButtonBox = QDialogButtonBox()
        verticalButtonBox.setOrientation(Qt.Vertical)
        verticalButtonBox.addButton(self.addButton, QDialogButtonBox.ActionRole)
        verticalButtonBox.addButton(self.removeButton, QDialogButtonBox.ActionRole)     
        verticalButtonBox.clicked.connect(self._verticalButtonBoxClickedEvent)
     
        # accept & cancel buttonbox
        self.acceptButton = QPushButton(self.tr('Accept'), self)
        self.acceptButton.setIcon(QIcon(':images/accept.png'))
        self.acceptButton.setEnabled(False)
        self.cancelButton = QPushButton(self.tr('Cancel'), self)
        self.cancelButton.setIcon(QIcon(':images/cancel.png'))
        horizontalButtonBox = QDialogButtonBox()
        horizontalButtonBox.addButton(self.acceptButton, QDialogButtonBox.AcceptRole)
        horizontalButtonBox.addButton(self.cancelButton, QDialogButtonBox.RejectRole)
        horizontalButtonBox.accepted.connect(self._acceptButtonAcceptedEvent)
        horizontalButtonBox.rejected.connect(lambda: self.reject())

        # main
        hbox = QHBoxLayout()
        hbox.setContentsMargins (0, 0, 0, 0)
        hbox.addWidget(self.favFoldersView)
        hbox.addWidget(verticalButtonBox)
        wbox = QWidget()
        wbox.setContentsMargins (0, 0, 0, 0)
        wbox.setLayout(hbox)
        vbox = QVBoxLayout()
        vbox.addWidget(wbox)
        vbox.addWidget(horizontalButtonBox)
        self.setLayout(vbox)
        self.setWindowTitle(self.tr('Favorite Folders'))
        self.setMinimumSize(400, 150)
        self.resize(500, 200)
        self._treeViewclickedEvent()

