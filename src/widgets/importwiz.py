from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.images_rc
import sys

class QImportWiz(QDialog):

    #
    # private
    #
    
    def _getCheckableList(self, sheets):
        """return an instance model with a sheet list composed of
           three columns (sheet, number of rows, number of columns)
        """
        model = QStandardItemModel(len(sheets), 3)
        model.setHeaderData(0, Qt.Horizontal, self.tr('Sheet'))
        model.setHeaderData(1, Qt.Horizontal, self.tr('Rows'))
        model.setHeaderData(2, Qt.Horizontal, self.tr('Columns'))
        for index, value in enumerate(sheets):
            # get data
            key = value[1]            
            numRows = value[2]
            numColumns = value[3]
            rowEnabled = numRows*numColumns>0
            # key column
            item = QStandardItem(key)
            if len(sheets) == 1:
                check = Qt.Checked
            else:
                check = Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            item.setEditable (False)
            item.setSelectable (False)
            item.setEnabled(rowEnabled)
            item.setData(key)
            model.setItem (index, 0, item)
            # num rows column
            item =QStandardItem(str(numRows))
            item.setEditable (False)
            item.setSelectable (False)
            item.setEnabled(rowEnabled)
            item.setData(key)
            model.setItem (index, 1, item)
            # num columns column
            item =QStandardItem(str(numColumns))
            item.setEditable (False)
            item.setSelectable (False)
            item.setEnabled(rowEnabled)
            item.setData(key)
            model.setItem(index, 2, item)
        return model

    def _viewClicked(self):
        sheets = self.sheets() 
        self.acceptButton.setEnabled(bool(sheets))

    #
    # public
    #
    
    def sheets(self):
        """returns key list of selected sheets"""
        selects = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            if item.checkState() == Qt.Checked:
                key = item.data().toString()
                selects.append(str(key))
        return selects
    
    #
    # init
    #
    
    def __init__(self, sheets, *args):
        QDialog.__init__ (self, *args)

        self.acceptButton = QPushButton(self.tr('Accept'), self)
        self.acceptButton.setIcon(QIcon(':images/accept.png'))
        self.cancelButton = QPushButton(self.tr('Cancel'), self)
        self.cancelButton.setIcon(QIcon(':images/cancel.png'))
        
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(lambda: self.accept())
        buttonBox.rejected.connect(lambda: self.reject())
        
        self.model = self._getCheckableList(sheets)
        view = QTreeView()
        view.setRootIsDecorated(False)
        view.setModel(self.model)
        view.resizeColumnToContents(0)
        view.resizeColumnToContents(1)
        view.resizeColumnToContents(2)
        view.clicked.connect(self._viewClicked)
        self._viewClicked()
        
        vbox = QVBoxLayout()
        vbox.addWidget(view)
        vbox.addWidget(buttonBox)
       
        self.setLayout(vbox)
        self.setWindowTitle(self.tr('Import Excel'))
        self.setMinimumSize(300, 250)
        self.resize(300, 250)

