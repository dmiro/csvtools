from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qlabelclickable import QLabelClickable
from widgets.helpers.qelidedlabel import QElidedLabel
from lib.pointsizes import Pointsizes
import sys
import lib.images_rc

class QStatus(QStatusBar):

    #
    # private
    #

    def __setPointSizeValue(self, value):
        if value:
            self.slider.setValue(value)
        else:
            self.slider.setValue(Pointsizes.normal())

    def __setLabelValue(self, labelWidget, stringFormat, value):
        if value:
            labelWidget.setText(stringFormat.format(value))
            labelWidget.setVisible(True)
            self.sliderWidget.setEnabled(True)
        else:
            labelWidget.setText('')
            labelWidget.setVisible(False)

    def __setLabelToolTip(self, labelWidget, stringFormat, value):
        if value:
            labelWidget.setToolTip(stringFormat.format(value))
            labelWidget.setVisible(True)
            self.sliderWidget.setEnabled(True)
        else:
            labelWidget.setToolTip('')
            labelWidget.setVisible(False)

    #
    # event
    #

    def __sliderValueChangedEvent(self, value):
        pointSize = self.slider.value()
        self.changedFontSize.emit(pointSize)
        self.percent.setText('{0:d}%'.format(Pointsizes.percentage(pointSize)))

    def __miniconClickedEvent(self):
        value = self.slider.value()
        self.slider.setValue(value - 1)

    def __maxiconClickedEvent(self):
        value = self.slider.value()
        self.slider.setValue(value + 1)

    #
    # public
    #

    changedFontSize = pyqtSignal(int)

    def setValues(self, linesValue, columnsValue, sizeValue, encodingValue,
                  modifiedValue, itemsValue, averageValue, sum_Value, pointSize):
        self.sliderWidget.setEnabled(False)
        self.__setLabelValue(self.lines, '  Lines={0:d}  ', linesValue)
        self.__setLabelValue(self.columns, '  Columns={0:d}  ', columnsValue)
        self.__setLabelValue(self.size, '  Size={0:s}  ', sizeValue)
        self.__setLabelValue(self.encoding, '  Encoding={0:s}  ', encodingValue)
        self.__setLabelValue(self.modified, '  Modified={0:s}  ', modifiedValue)
        self.__setLabelValue(self.average, '  Average={0:.2f}  ', averageValue)
        self.__setLabelToolTip(self.average, 'Average={0:f}', averageValue)
        self.__setLabelValue(self.items, '  Items={0:d}  ', itemsValue)
        self.__setLabelValue(self.sum_, '  Sum={0:.2f}  ', sum_Value)
        self.__setLabelToolTip(self.sum_, 'Sum={0:f}', sum_Value)
        self.__setPointSizeValue(pointSize)

    #
    # init
    #

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(Pointsizes.min(), Pointsizes.max())
        self.slider.setTickInterval(1)
        self.slider.setValue(Pointsizes.normal())
        self.slider.setSingleStep(1)
        self.slider.setFixedWidth(100)
        self.slider.setToolTip(self.tr('Ajustar nivel de escala'))
        self.slider.valueChanged.connect(self.__sliderValueChangedEvent)

        # min button slider
        self.minicon = QLabelClickable()
        self.minicon.setPixmap(QPixmap(':images/min.png').scaled(12, 12, Qt.KeepAspectRatio))
        self.minicon.clicked.connect(self.__miniconClickedEvent)

        # max button slider
        self.maxicon = QLabelClickable()
        self.maxicon.setPixmap(QPixmap(':images/max.png').scaled(12, 12, Qt.KeepAspectRatio))
        self.maxicon.clicked.connect(self.__maxiconClickedEvent)

        # slider + zoom in/out buttons
        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.addWidget(self.minicon)
        self.sliderLayout.addWidget(self.slider)
        self.sliderLayout.addWidget(self.maxicon)
        self.sliderLayout.setContentsMargins(0, 0, 0, 0)
        self.sliderWidget = QWidget()
        self.sliderWidget.setLayout(self.sliderLayout)
        self.sliderWidget.setFixedWidth(135)

        # labels
        self.lines= QElidedLabel('', width=0)
        self.columns= QElidedLabel('', width=0)
        self.size= QElidedLabel('', width=0)
        self.encoding = QElidedLabel('', width=0)
        self.modified= QElidedLabel('', width=0)
        self.items= QElidedLabel('', width=0)
        self.sum_= QElidedLabel('', width=0)
        self.average= QElidedLabel('', width=0)
        self.addWidget(self.lines)
        self.addWidget(self.columns)
        self.addWidget(self.size)
        self.addWidget(self.encoding)
        self.addWidget(self.modified)
        self.addWidget(self.items)
        self.addWidget(self.sum_)
        self.addWidget(self.average)

        # zoom
        self.percent = QLabel()
        pointSize = self.slider.value()
        self.percent.setText('{0:d}%'.format(Pointsizes.percentage(pointSize)))

        self.percent.setFixedWidth(35)
        self.addPermanentWidget(self.sliderWidget)
        self.addPermanentWidget(self.percent)

        # layout
        self.setContentsMargins(0, 0, 0, 0)

        # init
        self.setValues(None, None, None, None, None, None, None, None, None)
