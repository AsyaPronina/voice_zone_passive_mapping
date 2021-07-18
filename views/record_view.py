from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QPushButton, QTextEdit
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QIcon, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QLine, QRect, QRectF, QSize, QPointF, QTime, pyqtSlot

class RecordView(QWidget):
    def __init__(self, number, label):
        super().__init__()
        self.number = number
        self.label = label
        self.startTime = None
        self.endTime = None
        self.invalid = False

    def paintText(self, painter, pos, font, brush, text):
        textPath = QPainterPath()
        textPath.addText(pos, font, text)
        painter.fillPath(textPath, brush)

    def paintLine(self, painter, pen, startPos, endPos):
        linePath = QPainterPath(startPos)
        linePath.lineTo(endPos)
        painter.strokePath(linePath, pen)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(0), 0.2)
        painter.setPen(pen)

        brush = QBrush(QColor(16777215))
        painter.setBrush(brush)

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 2, -2, -2)
        #may be to not round?
        path.addRoundedRect(rect, 15, 15)

        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

        gothicFont = QFont("Century Gothic", 10)
        smallGothicFont = QFont("Century Gothic", 9)
        intelFont = QFont("IntelOne Display Light", 10)
        lightGrayBrush = QBrush(QColor(10526880))
        darkGrayBrush = QBrush(QColor(4210494))
        if self.invalid:
            darkGrayBrush = QBrush(QColor(11776688))

        ######################## Print entry number ##########################
        pos = (rect.topLeft() + rect.bottomLeft()) / 2 + QPointF(15., 3)
        self.paintText(painter, pos, gothicFont, lightGrayBrush, str(self.number))
        numHeight = QFontMetrics(gothicFont).boundingRect(str(self.number)).height()
        numWidth = QFontMetrics(gothicFont).boundingRect(str(self.number)).width()
        if self.invalid:
            middlePos = pos - QPointF(0, numHeight / 3)
            crossNumStartPos = middlePos + QPointF(- numWidth / 2, 0)
            crossNumEndPos = middlePos + QPointF(numWidth * 1.5, 0)
            self.paintLine(painter, QPen(QColor(16725326), 0.4), crossNumStartPos, crossNumEndPos)

        # check slot for class and re-configure if what
        ######################## Print label and duration if entry is valid and "invalid" otherwise ##########################
        duration = QTime(0, 0)
        duration = duration.addMSecs(self.startTime.msecsTo(self.endTime))
        durationString = '(' + duration.toString() + ')'

        classWidth = QFontMetrics(intelFont).boundingRect(self.label).width()
        classPos = (rect.topLeft() + rect.topRight()) / 2 + QPointF(- classWidth / 2, 16)
        self.paintText(painter, classPos, intelFont, darkGrayBrush, self.label) #QBrush(QColor(10066592))

        durationWidth = QFontMetrics(smallGothicFont).boundingRect(durationString).width()
        classHeight = QFontMetrics(intelFont).boundingRect(self.label).height()
        durationPos = (rect.topLeft() + rect.topRight()) / 2 + QPointF(- durationWidth / 2, 15 + classHeight)
        if not self.invalid:
            self.paintText(painter, durationPos, smallGothicFont, QBrush(QColor(10066592)), durationString) #QBrush(QColor(10066592))
        else:
            invalidWidth = QFontMetrics(intelFont).boundingRect("invalid  record").width()
            invalidPos = (rect.topLeft() + rect.topRight()) / 2 + QPointF(- invalidWidth / 2, 13 + classHeight)
            self.paintText(painter, invalidPos, intelFont, QBrush(QColor(16725326)), "invalid  record") #QBrush(QColor(10066592))

        ######################## Draw timeline ##########################
        timelineRect = QRectF(self.rect())
        #magick number 30 allows to narrow line
        timelineRect = timelineRect.adjusted(40, 0, - 40, 0)
        durationHeight = QFontMetrics(gothicFont).boundingRect(durationString).height()
        startPos = (timelineRect.topLeft() + timelineRect.bottomLeft()) / 2 + QPointF(0, durationHeight - 4)
        endPos = (timelineRect.topRight() + timelineRect.bottomRight()) / 2 + QPointF(0, durationHeight - 4)
        self.paintLine(painter, QPen(QColor(0), 0.2), startPos + QPointF(10, 0), endPos - QPointF(10, 0))
        self.paintLine(painter, QPen(QColor(0), 0.2), startPos + QPointF(9, -2), startPos + QPointF(9, 2))
        self.paintLine(painter, QPen(QColor(0), 0.2), endPos - QPointF(9, 2), endPos - QPointF(9, -2)) 

        ######################## Print start and end timestamps ##########################
        self.paintText(painter, startPos + QPointF(0, -6), gothicFont, darkGrayBrush, self.startTime.toString())
        endTimeString = self.endTime.toString()
        endTimeWidth = QFontMetrics(gothicFont).boundingRect(endTimeString).width()
        self.paintText(painter, endPos + QPointF(- endTimeWidth, -6), gothicFont, darkGrayBrush, endTimeString)

        ######################## Gray out and print "invalid" in case if entry is invalid  ##########################
        if self.invalid:
            count = int(timelineRect.size().width() / 35)

            interval = 35
            for i in range(0, count, 1):
                crossStartPos = timelineRect.topLeft() + QPointF(i * interval, 3)
                crossEndPos = timelineRect.bottomLeft() + QPointF(i * interval + 30, -3)
                self.paintLine(painter, QPen(QColor(16725326), 0.5, Qt.PenStyle.DotLine), crossStartPos, crossEndPos)

    def setStartTime(self, startTime):
        self.startTime = startTime

    def setEndTime(self, endTime):
        self.endTime = endTime

    def invalidate(self):
        self.invalid = True