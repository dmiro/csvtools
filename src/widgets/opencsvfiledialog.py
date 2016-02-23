from PyQt4.QtGui import *
from PyQt4.QtCore import *


class QOpenCsvFileDialog(QFileDialog):

    #
    # public
    #

    def useWizard(self):
        return self.checkboxWizard.checkState() == Qt.Checked
    #
    # init
    #
    
    def __init__(self, *args):
        super(QOpenCsvFileDialog, self).__init__(caption='Open File', *args)
        # caption='Open File', 
        self.setViewMode(QFileDialog.Detail);
        self.setFileMode(QFileDialog.ExistingFile)
        self.setNameFilters(['Csv Files (*.csv)','All Files (*)']);
        self.setOptions(QFileDialog.ReadOnly)
        layout = self.layout()
        self.checkboxWizard = QCheckBox(self.tr('Use Wizard'))
        self.checkboxWizard.setStyleSheet("background-color: yellow; font: bold")
        if layout:                
            layout.addWidget(self.checkboxWizard, 4, 2)

    #
    # static
    #
    
    @staticmethod
    def getOpenFileName(parent = None):
        dialog = QOpenCsvFileDialog(parent)
        dialog.exec_()
        filename = ''
        selectedFiles = dialog.selectedFiles()
        if selectedFiles:
            if len(selectedFiles) > 0:
                filename = str(selectedFiles[0])       
        return filename, dialog.useWizard()


#
# test
#

if __name__ == '__main__':
    
    import sys
    app = QApplication(sys.argv)
    filename, useWizard = QOpenCsvFileDialog.getOpenFileName()
    print 'filename:', filename
    print 'useWizard:', useWizard
    sys.exit(app.exec_())
