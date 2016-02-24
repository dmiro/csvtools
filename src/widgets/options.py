from PyQt4 import QtCore, QtGui
import lib.images_rc
import sys
import ConfigParser

class Options(QtGui.QDialog):

    def acceptDialog(self):
        config = ConfigParser.ConfigParser()
        config.read('csvreader.ini')
        if not config.has_section('config'):
            config.add_section('config')
        config.set('config', 'path', '/var/shared/')
        config.set('config', 'default_message', 'Hey! help me!!')
        with open('csvreader.ini', 'wb') as configfile:
            config.write(configfile)
        self.accept()

    def cancelDialog(self):
        self.accept()

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)

        accept = QtGui.QPushButton(self.tr('Accept'), self)
        accept.setIcon(QtGui.QIcon(':images/accept.png'))
        accept.clicked.connect(self.acceptDialog)

        cancel = QtGui.QPushButton(self.tr('Cancel'), self)
        cancel.setIcon(QtGui.QIcon(':images/cancel.png'))
        cancel.clicked.connect(self.cancelDialog)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(accept)
        hbox.addWidget(cancel)

        self.language = QtGui.QComboBox()
        self.autodetect = QtGui.QCheckBox('')

        grid = QtGui.QFormLayout()
        grid.addRow(self.tr('Language'), self.language)
        grid.addRow(self.tr('Detect format'), self.autodetect)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch()
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle(self.tr('Options'))
        #self.setFixedSize(225, 175)





