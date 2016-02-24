from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.images_rc


class QReport(QDialog):

    #
    # init
    #

    def __init__(self, lines, *args):
        QDialog.__init__ (self, *args)

        if isinstance(lines, basestring):
            lines = [lines]
        info = QLabel('<br/>'.join(lines))

        scrollArea = QScrollArea()
        scrollArea.setBackgroundRole(QPalette.Light)
        scrollArea.setWidget(info)

        acceptButton = QPushButton(self.tr('Accept'), self)
        acceptButton.setIcon(QIcon(':images/accept.png'))

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(acceptButton, QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(lambda: self.accept())

        vbox = QVBoxLayout()
        vbox.addWidget(scrollArea)
        vbox.addWidget(buttonBox)

        self.setLayout(vbox)
        self.setWindowTitle(self.tr('Report'))
        self.setMinimumSize(600, 150)
        self.resize(600, 150)

