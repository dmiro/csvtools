from PyQt4.QtCore import *
from PyQt4.QtGui import *
from helpers.qradiobuttongroup import QRadioButtonGroup
from helpers.qcheckboxgroup import QCheckGroupBox
from widgets.csvm import QCsv
from lib.document import Csv
import sys


class DelimiterGroupBox(QRadioButtonGroup):

    #
    # public
    #
   
    def value(self):
        index = self.selectedItem()
        if index == 0:
            return ','
        elif index == 1:
            return ';'
        elif index == 2:
            return '\t'
        elif index == 3:
            return ' '
        else:
            return self.buddie(4).text()

    #
    # init
    #
    
    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Delimiter', columns=1)
        self.addItem(self.tr('Comma (,)'))
        self.addItem(self.tr('Semicolon (;)'))
        self.addItem(self.tr('Tab'))
        self.addItem(self.tr('Space'))
        self.addItem(self.tr('Other'), widget=QLineEdit())


class QuoteGroupBox(QRadioButtonGroup):

    #
    # public
    #
   
    def value(self):
        index = self.selectedItem()
        if index == 0:
            return ''
        elif index == 1:
            return '"'
        elif index == 2:
            return '\''
        else:
            return self.buddie(3).text()
      
    #
    # init
    #
    
    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Quote Char', columns=1)
        self.addItem(self.tr('None'))
        self.addItem(self.tr('Double quote (")'))
        self.addItem(self.tr('Quote (\')'))
        self.addItem(self.tr('Other'), widget=QLineEdit())


class LineTerminatorGroupBox(QRadioButtonGroup):

    #
    # public
    #
   
    def value(self):
        index = self.selectedItem()
        if index == 0:
            return '\\r\\n'
        else:
            return self.buddie(1).text()
      
    #
    # init
    #
    
    def __init__(self):
        QRadioButtonGroup.__init__ (self, title='Line Terminator', columns=1)
        self.addItem(self.tr('\\r\\n'))
        self.addItem(self.tr('Other'), widget=QLineEdit())

     
class AdjustsGroupBox(QCheckGroupBox):

    #
    # public
    #

    def isSkipInitialSpace(self):
        return 0 in self.selectedItems()
        
    def isSkipEmptyLines(self):
        return 1 in self.selectedItems()
         
    def isHeaderRow(self):
        return 2 in self.selectedItems()
         
    def isSkipEmptyColumns(self):
        return 3 in self.selectedItems()

    #
    # init
    #
    
    def __init__(self):
        QCheckGroupBox.__init__ (self, title='Adjusts', columns=2)
        self.addItem(self.tr('Skip initial space'))       
        self.addItem(self.tr('Skip empty lines'))        
        self.addItem(self.tr('Header row'))        
        self.addItem(self.tr('Skip empty columns'))
       

class QCsvWiz(QDialog):
 
    #
    # widgets
    #
    
    def _addButtonBox(self):
        acceptButton = QPushButton(self.tr('Accept'), self)
        acceptButton.setIcon(QIcon(':images/accept.png'))
        cancelButton = QPushButton(self.tr('Cancel'), self)
        cancelButton.setIcon(QIcon(':images/cancel.png'))    
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(lambda: self.accept())
        buttonBox.rejected.connect(lambda: self.reject())
        return buttonBox
  
    def _addPreviewGroupBox(self):
        groupBox = QGroupBox(self.tr('Preview'), parent=self)
        formLayout = QFormLayout(parent=groupBox)
        # Preview TableView
        self.preview = QCsv(Csv(self.filename))
        self.preview.setEnabled(False)
        formLayout.addRow(self.preview)        
        return groupBox

    #
    # slots
    #
    
    def _groupBoxClickedSlot(self):
        print self.delimiterGroupBox.value()
        print self.quoteGroupBox.value()
        print self.adjustsGroupBox.isSkipInitialSpace()
        print self.adjustsGroupBox.isSkipEmptyLines()
        print self.adjustsGroupBox.isHeaderRow()
        print self.adjustsGroupBox.isSkipEmptyColumns()
        print self.lineTerminatorGroupBox.value()
        csv = Csv(self.filename,
                  delimiter =self.delimiterGroupBox.value())
        self.preview.setDocument(csv)

        ##self.preview.data = data

       # self.preview.setEnabled(False)


    #
    # init
    #

    def __init__(self, filename, *args):
        QDialog.__init__ (self, *args)
        self.filename = filename

        # widgets
        self.buttonBox = self._addButtonBox()
        self.delimiterGroupBox = DelimiterGroupBox()
        self.quoteGroupBox = QuoteGroupBox()
        self.adjustsGroupBox = AdjustsGroupBox()
        self.lineTerminatorGroupBox = LineTerminatorGroupBox()
        self.previewGroupBox = self._addPreviewGroupBox()

        # signals
        self.delimiterGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.quoteGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.adjustsGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)
        self.lineTerminatorGroupBox.selectItemChanged.connect(self._groupBoxClickedSlot)

        # layout
        grid = QGridLayout()
        grid.addWidget(self.delimiterGroupBox, 0, 0, 2, 1)
        grid.addWidget(self.quoteGroupBox, 0, 1, 2, 1)
        grid.addWidget(self.adjustsGroupBox, 0, 2)
        grid.addWidget(self.lineTerminatorGroupBox, 1, 2)
        grid.addWidget(self.previewGroupBox, 2, 0, 1, 3)
        grid.addWidget(self.buttonBox, 3, 0, 1, 3)

        # main
        self.setLayout(grid)
        self.setWindowTitle(self.tr('Import Csv'))
        self.setFixedSize(800, 400)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QCsvWiz(filename='..\..\testdocs\demo4.csv')
    w.show()
    sys.exit(app.exec_())
