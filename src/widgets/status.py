from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widgets.helpers.qlabelclickable import QLabelClickable
from widgets.helpers.qelidedlabel import QElidedLabel
import sys
import lib.images_rc

# Standard font point sizes
PointSizes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]

class QStatus(QStatusBar):

    #
    # private
    #

    def _normalFontSize(self):
        """get normal fontsize"""
        return PointSizes[self.normalIndexSize-1]

    def _fontSize(self):
        """get current fontsize"""
        return PointSizes[self.slider.value()-1]

    def _percentageFontSize(self):
        """get percentage fontsize"""
        return (self._fontSize()*100) / self._normalFontSize()

    def _setLabelValue(self, labelWidget, stringFormat, value):
        if value:
            labelWidget.setText(stringFormat.format(value))
            labelWidget.setVisible(True)
            self.sliderWidget.setEnabled(True)
        else:
            labelWidget.setText('')
            labelWidget.setVisible(False)

    def _setLabelToolTip(self, labelWidget, stringFormat, value):
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

    def _sliderValueChangedEvent(self, value):
        self.changedFontSize.emit(self._fontSize())
        self.percent.setText('{0:d}%'.format(self._percentageFontSize()))

    def _miniconClickedEvent(self):
        value = self.slider.value()
        self.slider.setValue(value-1)

    def _maxiconClickedEvent(self):
        value = self.slider.value()
        self.slider.setValue(value+1)

    #
    # public
    #

    changedFontSize = pyqtSignal(int)

    def setValues(self, linesValue, columnsValue, sizeValue, modifiedValue, itemsValue, averageValue, sum_Value):
        self.sliderWidget.setEnabled(False)
        self._setLabelValue(self.lines, '  Lines={0:d}  ', linesValue)
        self._setLabelValue(self.columns, '  Columns={0:d}  ', columnsValue)
        self._setLabelValue(self.size, '  Size={0:s}  ', sizeValue)
        self._setLabelValue(self.modified, '  Modified={0:s}  ', modifiedValue)
        self._setLabelValue(self.average, '  Average={0:.2f}  ', averageValue)
        self._setLabelToolTip(self.average, 'Average={0:f}', averageValue)
        self._setLabelValue(self.items, '  Items={0:d}  ', itemsValue)
        self._setLabelValue(self.sum_, '  Sum={0:.2f}  ', sum_Value)
        self._setLabelToolTip(self.sum_, 'Sum={0:f}', sum_Value)

    #
    # init
    #

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.normalIndexSize = PointSizes.index(QFont().pointSize())

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, len(PointSizes))
        self.slider.setTickInterval(1)
        self.slider.setValue(self.normalIndexSize+1)
        self.slider.setSingleStep(1)
        self.slider.setFixedWidth(100)
        self.slider.setToolTip(self.tr('Ajustar nivel de escala'))
        self.slider.valueChanged.connect(self._sliderValueChangedEvent)

        # min button slider
        self.minicon = QLabelClickable()
        self.minicon.setPixmap(QPixmap(':images/min.png').scaled(12, 12, Qt.KeepAspectRatio))
        self.minicon.clicked.connect(self._miniconClickedEvent)

        # max button slider
        self.maxicon = QLabelClickable()
        self.maxicon.setPixmap(QPixmap(':images/max.png').scaled(12, 12, Qt.KeepAspectRatio))
        self.maxicon.clicked.connect(self._maxiconClickedEvent)

        # slider + min & max buttons
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
        self.modified= QElidedLabel('', width=0)
        self.items= QElidedLabel('', width=0)
        self.sum_= QElidedLabel('', width=0)
        self.average= QElidedLabel('', width=0)
        self.addWidget(self.lines)
        self.addWidget(self.columns)
        self.addWidget(self.size)
        self.addWidget(self.modified)
        self.addWidget(self.items)
        self.addWidget(self.sum_)
        self.addWidget(self.average)

        # zoom
        self.percent= QLabel('100%')
        self.percent.setFixedWidth(35)
        self.addPermanentWidget(self.sliderWidget)
        self.addPermanentWidget(self.percent)

        # layout
        self.setContentsMargins(0, 0, 0, 0)

        # init
        self.setValues(None, None, None, None, None, None, None)
