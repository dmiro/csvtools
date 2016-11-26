# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qlabelclickable import QLabelClickable

import lib.images_rc
import webbrowser

__version_info__ = (0, 0, 9)
__version__ = '.'.join(str(v) for v in __version_info__)


class QAbout(QDialog):

    TITLE = """<font style="font-size: 24pt; color: black; font-family: Sans-Serif">CSV</font>
<font style="font-size: 24pt; color: green; font-family: Sans-Serif"> Tools</font>"""

    AUTHOR = """Author:  David Miró"""

    HOMEPAGE = """Home Page:&nbsp;&nbsp;<a href="http://www.3engine.net">http://www.3engine.net</a>"""

    VERSION = """Version: """ + __version__

    BUILDTIME = """<font style="font-size: 10px; color: gray">Build time:  03/11/2015 - 10:33:25</font>"""

    LICENSE = """This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA."""

    #
    # private
    #
    def _homepageClicked(self):
        webbrowser.open('http://www.3engine.net')

    #
    # init
    #

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        # add widgets
        self.buildTime = QLabel(self.BUILDTIME)
        self.title = QLabel(self.TITLE)
        self.author = QLabel(self.AUTHOR)
        self.homepage = QLabelClickable(self.HOMEPAGE)
        self.homepage.setToolTip('go to homepage')
        self.homepage.clicked.connect(self._homepageClicked)
        self.version = QLabel(self.VERSION)
        self.license_ = QLabel(self.LICENSE)
        self.license_.setWordWrap(True)
        self.license_.setFixedWidth (360)
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Light)
        self.scrollArea.setWidget(self.license_)
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaLayout.addWidget(self.scrollArea)
        self.scrollAreaGroupBox = QGroupBox('GNU General Public License')
        self.scrollAreaGroupBox.setLayout(self.scrollAreaLayout)
        self.scrollAreaGroupBox.setAlignment(Qt.AlignHCenter)

        # button box widget
        self.acceptButton = QPushButton(self.tr('Accept'), self)
        self.acceptButton.setIcon(QIcon(':images/accept.png'))
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.acceptButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.accepted.connect(lambda: self.accept())

        # central widget
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.buildTime, alignment=Qt.AlignRight)
        self.vbox.addWidget(self.title)
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.author)
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.homepage)
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.version)
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.scrollAreaGroupBox)
        self.vbox.addSpacing(10)
        self.vbox.addStretch()
        self.vbox.addWidget(self.buttonBox)

        # dialog widget
        self.setLayout(self.vbox)
        self.setWindowTitle(self.tr('About'))
        self.setFixedSize(425, 350)
        # enable custom window hint
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        # removes context help button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # disables (but not hide) close button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        # disables title frame
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowTitleHint)


