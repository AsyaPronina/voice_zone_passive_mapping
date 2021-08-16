import PyQt6
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QStyle, QStyleOption, QSizePolicy
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QPixmap
from PyQt6.QtCore import QRect, QRectF, QSize, QMargins, QTimer, pyqtSlot

import enum

class PictureView(QWidget):
    class State(enum.Enum):
        Init = 0
        Paused = 1
        Playing = 2

    def __init__(self, viewmodel):
        super().__init__()

        self.state = PictureView.State.Init

        uic.loadUi(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\views\picture_view.ui', self)
        self.setWindowOpacity(1.0)
        self.setAutoFillBackground(True)
        pal = QPalette(QColor(14079702))
        self.setPalette(pal)

        self.pictureLabel.setUpdatesEnabled(True)
        self.pictureLabel.setAlignment(PyQt6.QtCore.Qt.Alignment.AlignTop | PyQt6.QtCore.Qt.Alignment.AlignHCenter)
        self.pixmap = None

        self.timerLabel = QLabel()
        self.horizontalLayout.addWidget(self.timerLabel, 1, PyQt6.QtCore.Qt.Alignment.AlignCenter)
        self.horizontalLayout.setContentsMargins(5, 10, 5, 5)
        self.timerLabel.setContentsMargins(5, 5, 5, 5)
        self.timerLabel.setUpdatesEnabled(True)
        self.updateTimerLabel(0)

        self.secondsForPicture = viewmodel.timeout()
        self.perSecTimer = QTimer()
        self.interval = 1000
        self.perSecTimer.setInterval(self.interval)
        self.perSecTimer.timeout.connect(self.handleSecondPassed)

        # margins are set by designer, but it is better to set them via Style

        #vm.nextPicture.connect(self.handleNextPicture) ?? PyQt6.QtCore.Qt.ConnectionType.QueuedConnection
        #this will be remote timer from remote host in future.  
        self.viewmodel = viewmodel
        self.viewmodel.timeoutUpdated.connect(self.handleTimeoutUpdated)
        self.viewmodel.paused.connect(self.handlePaused)
        self.viewmodel.playing.connect(self.handlePlaying)
        self.viewmodel.nextPicture.connect(self.handleNextPicture)
        self.viewmodel.endOfStream.connect(self.handleEndOfStream)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(8553090), 0.5)
        painter.setPen(pen)
        brush = QBrush(QColor(15395562))
        painter.setBrush(brush)

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(rect, 35, 35)

        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

    @pyqtSlot()
    def handleSecondPassed(self):
        print("pictures: 1 sec")

        if self.perSecTimer.isSingleShot():
            self.perSecTimer.setInterval(self.interval)
            self.perSecTimer.setSingleShot(False)
            self.perSecTimer.start()

        self.secondsForPicture -= 1
        self.updateTimerLabel(self.secondsForPicture)

    @pyqtSlot()
    def handleTimeoutUpdated(self):
        print("pictures: timeout updated")
        print(self.viewmodel.timeout())
        self.secondsForPicture = self.viewmodel.timeout()

    @pyqtSlot()
    def handlePlaying(self):
        print("pictures: playing")
        self.perSecTimer.start()
        self.state = PictureView.State.Playing

    @pyqtSlot()
    def handlePaused(self):
        print("pictures: paused")
        interval = self.perSecTimer.remainingTime()
        self.perSecTimer.setInterval(interval)
        self.perSecTimer.setSingleShot(True)
        self.perSecTimer.stop()
        self.state = PictureView.State.Paused

    #setScaledContents =  true shows much better quality
    @pyqtSlot()
    def handleNextPicture(self):
        print('pictures: Next picture')

        self.secondsForPicture = self.viewmodel.timeout()
        self.updateTimerLabel(self.secondsForPicture)
        self.pixmap = QPixmap(self.viewmodel.picturePath())
        self.adjustPixmapToWidgetSize()

        assert(self.state == PictureView.State.Playing or self.state == PictureView.State.Paused)
        if self.state == PictureView.State.Playing:
            self.perSecTimer.start()
        else:
            # we need to count seconds anew for new picture if state is paused and timer has part of second
            if self.perSecTimer.isSingleShot():
                #logic repeats handleSecondPassed --> needs to retrieve to one place.
                self.perSecTimer.setInterval(self.interval)
                self.perSecTimer.setSingleShot(False)

    @pyqtSlot()
    def handleEndOfStream(self):
        print('pictures: no pictures left')
        self.secondsForPicture = self.viewmodel.timeout()
        self.updateTimerLabel(0)
        self.perSecTimer.stop()

        self.pixmap = QPixmap()
        self.pictureLabel.setPixmap(self.pixmap)

        self.state = PictureView.State.Init

    def resizeEvent(self, event):
        self.adjustPixmapToWidgetSize()

    def updateTimerLabel(self, seconds):
        secondsInDay = 60 * 60 * 24
        secondsInHour = 60 * 60
        secondsInMinute = 60

        days = seconds // secondsInDay
        hours = (seconds - (days * secondsInDay)) // secondsInHour
        minutes = (seconds - (days * secondsInDay) - (hours * secondsInHour)) // secondsInMinute
        seconds = seconds - (days * secondsInDay) - (hours * secondsInHour) - (minutes * secondsInMinute)

        stringify = lambda x : '0' + str(x) if x < 10 else str(x)

        text = stringify(hours) + ':' + stringify(minutes) + ':' + stringify(seconds)

        self.timerLabel.setText("<html><head><meta name=\"qrichtext\" content=\"1\" /></head>"
                                "<body style=\" white-space: pre-wrap; font-family:Century Gothic; "
                                "font-size:9pt; font-weight:10; font-style:normal; text-decoration:none;\">"
                                "<p style=\" margin-top:10px; margin-bottom:0px; margin-left:0px; "
                                "margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size: 20pt; color: #b0b0b0;\">"
                                + text +"</p>"
                                "</body></html>")

    #setScaledContents =  true shows much better quality
    def adjustPixmapToWidgetSize(self):
        rect = self.gridLayout.cellRect(1, 0)
        rect.adjust(15, 15, -15, -15)

        if self.pixmap:
            scaledPixmap = self.pixmap.scaled(rect.size(), PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                           PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
            self.pictureLabel.setPixmap(scaledPixmap)
