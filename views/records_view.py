import time

import PyQt6
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette
from PyQt6.QtCore import QRect, QRectF, QSize, QPoint, QTimer, QTime, pyqtSlot

from record_view import RecordView

class RecordsView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.layout)

        self.listWidget = QListWidget()
        self.layout.addWidget(self.listWidget)

        # Need to narrow hover region to select the item
        self.listWidget.setStyleSheet("""
            QListWidget {
                background: #EAEAEA;
                border: 0px;
                padding: 10px;
                show-decoration-selected: 1;
            }
            QListWidget::item {
                background-color: #EAEAEA;
            }
            QListWidget::item:hover {
                border: 2px solid lightgray;
                border-radius: 16px;
            }
            QScrollBar:vertical {              
                border: none;
                background:white;
                width: 5px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130), stop:1 rgb(32, 47, 130));
                min-height: 0px;
            }
            QScrollBar::add-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }""")

        self.listWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.listWidget.setSpacing(10)

        self.number = 1
        self.lastRecordWidget = None
        #self.replayTimings = []
        self.timer = QTimer()
        self.interval = 50
        self.timer.setInterval(self.interval)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.handleTimeout)

        self.viewmodel = viewmodel
        self.viewmodel.playing.connect(self.handlePlaying)
        self.viewmodel.paused.connect(self.handlePaused)
        self.viewmodel.nextPicture.connect(self.handleNextPicture)
        self.viewmodel.endOfStream.connect(self.handleEndOfStream)
        self.viewmodel.experimentCleaned.connect(self.handleExperimentCleaned)

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

    def addRecordWidget(self, recordWidget):
        item = QListWidgetItem()
        item.setSizeHint(QSize(50, 50))
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, recordWidget)
        self.timer.start()

    @pyqtSlot()
    def handleInvalidateLastRecord(self):
        if self.lastRecordWidget != None:
            self.lastRecordWidget.invalidate()
        print('records: invalidate last record')

    @pyqtSlot()
    def selectionChanged(self):
        print("Selected items: ", self.listWidget.selectedItems())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    @pyqtSlot()
    def handleTimeout(self):
        self.listWidget.scrollToBottom()

    @pyqtSlot()
    def handlePlaying(self):
        print("records: playing")

    @pyqtSlot()
    def handlePaused(self):
        print("records: pause")

    @pyqtSlot()
    def handleNextPicture(self):
        if self.lastRecordWidget != None:
            self.lastRecordWidget.setEndTime(QTime.currentTime())
            self.addRecordWidget(self.lastRecordWidget)
        #is this truth for the paused state? seems yes, we are showing something.
        self.lastRecordWidget = RecordView(self.number, self.viewmodel.getActivePictureLabel())
        self.lastRecordWidget.setStartTime(QTime.currentTime())
        self.number += 1

    @pyqtSlot()
    def handleEndOfStream(self):
        if self.lastRecordWidget != None:
            self.lastRecordWidget.setEndTime(QTime.currentTime())
            self.addRecordWidget(self.lastRecordWidget)
        self.lastRecordWidget = None
        print("records: eos")

    @pyqtSlot()
    def handleExperimentCleaned(self):
        self.listWidget.clear()
        self.number = 1
        print("records: experiment cleaned")

