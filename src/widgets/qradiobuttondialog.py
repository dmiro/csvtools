from PyQt4.QtCore import *
from PyQt4.QtGui import *
from helpers.qradiobuttongroup import QRadioButtonGroup
import lib.images_rc

class QRadioButtonDialog(QDialog):

    #
    # public
    #
    def selectedItem(self):
        return self.radioButtonGroup.selectedItem()

    #
    # init
    #

    def __init__(self, title, items, columns=1, setIndex=0):
        super(QRadioButtonDialog, self).__init__()
        # add widgets
        self.radioButtonGroup = QRadioButtonGroup(title=title, columns=columns)
        for item in items:
            self.radioButtonGroup.addItem(item)
        self.radioButtonGroup.setChecked_(setIndex, True)
        # button box widget
        acceptButton = QPushButton(self.tr('Accept'), self)
        acceptButton.setIcon(QIcon(':images/accept.png'))
        cancelButton = QPushButton(self.tr('Cancel'), self)
        cancelButton.setIcon(QIcon(':images/cancel.png'))
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.accepted.connect(lambda: self.accept())
        buttonBox.rejected.connect(lambda: self.reject())
        # central widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.radioButtonGroup)
        vbox.addWidget(buttonBox)
        self.setLayout(vbox)
        self.setWindowTitle(title)
        # enable custom window hint
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        # removes context help button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # disables (but not hide) close button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        # non-resizeable dialog
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

    #
    # static
    #

    @staticmethod
    def getSelectItem(title, items):
        dialog = QRadioButtonDialog(title, items)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            return dialog.selectedItem()
        else:
            return -1

