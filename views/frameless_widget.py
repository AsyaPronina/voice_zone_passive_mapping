import enum
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit
from PyQt6.QtWidgets import QPushButton, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QStyle, QStyleOption
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QMouseEvent, QHoverEvent
from PyQt6.QtCore import QRect, QRectF, QSize, QPoint, QEvent, QMargins

from custom_border_draggers import LeftDragger, RightDragger, TopDragger, BottomDragger
from custom_border_draggers import TopLeftDragger, TopRightDragger, BottomLeftDragger, BottomRightDragger 

#May be used in inheritance and composition relationships.
#Not ideal logic(responsibilities) separation
class FramelessWidget(QWidget):
    class State(enum.Enum):
        Init = 0
        Moving = 1
        Resizing = 2

    def __init__(self, target = None):
        super().__init__()

        self.state = FramelessWidget.State.Init

        self.leftButtonPressed = False

        self.borderMargin = 5
        self.cornerMargin = 5
        self.activeBorderDragger = None
        self.borderDraggers = ( LeftDragger(), RightDragger(), TopDragger(), BottomDragger() )
        self.cornerDraggers = ( TopLeftDragger(), TopRightDragger(), BottomLeftDragger(), BottomRightDragger() )

        self.wholeWidgetDragPos = None

        self.target = target
        if not target:
            self.target = self
        self.target.setMouseTracking(True)
        self.target.setWindowFlags(QtCore.Qt.WindowFlags.FramelessWindowHint)
        self.target.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover)
        self.target.installEventFilter(self)

    def setBorderMargin(self, margin):
        self.borderMargin = margin

    def setCornerMargin(self, margin):
        self.cornerMargin = margin

    def selectActiveBorderDragger(self, pos):
        activeDragger = None
        for dragger in self.borderDraggers:
            if dragger.isActive(pos, self.target.frameGeometry(), self.borderMargin):
                activeDragger = dragger

        for dragger in self.cornerDraggers:
            if dragger.isActive(pos, self.target.frameGeometry(), self.cornerMargin):
                activeDragger = dragger

        return activeDragger

    def eventFilter(self, o, e):
        if  e.type() == QEvent.Type.MouseMove or \
            e.type() == QEvent.Type.HoverMove or \
            e.type() == QEvent.Type.Leave or \
            e.type() == QEvent.Type.MouseButtonPress or \
            e.type() == QEvent.Type.MouseButtonRelease:

            switcher = {
                QEvent.Type.MouseMove: self.mouseMove,
                QEvent.Type.HoverMove: self.mouseHover,
                QEvent.Type.Leave: self.mouseLeave,
                QEvent.Type.MouseButtonPress: self.mousePress,
                QEvent.Type.MouseButtonRelease: self.mouseRelease
            }

            switcher.get(e.type())(e)

            return True
        else:
            return super().eventFilter(o, e)

    def mousePress(self, event):
        if event.buttons() == QtCore.Qt.MouseButtons.LeftButton:
            self.leftButtonPressed = True

            self.activeBorderDragger = self.selectActiveBorderDragger(event.globalPosition())

            if self.activeBorderDragger is not None:
                self.state = FramelessWidget.State.Resizing
                self.target.update()
            elif self.target.rect().marginsRemoved(QMargins(self.borderMargin, \
                                                             self.borderMargin, \
                                                             self.borderMargin, \
                                                             self.borderMargin)) \
                    .contains(event.position().toPoint()):
                self.state = FramelessWidget.State.Moving
                self.target.update()
                self.wholeWidgetDragPos = event.position()

    def mouseMove(self, event):
        if self.leftButtonPressed:
            if self.state == FramelessWidget.State.Moving:
                self.target.move((event.globalPosition() - self.wholeWidgetDragPos).toPoint())
            elif self.state == FramelessWidget.State.Resizing:
                rect = self.target.frameGeometry()
                self.activeBorderDragger.updateGeometry(rect, event.globalPosition())

                if rect.width() <= self.target.minimumSize().width():
                    rect.setLeft(self.target.frameGeometry().x())
                if rect.height() <= self.target.minimumSize().height():
                    rect.setTop(self.target.frameGeometry().y())

                self.target.setGeometry(rect)

    def mouseHover(self, event):
        self.updateCursorShape(self.target.mapToGlobal(event.position()))

    def mouseLeave(self, event):
        self.target.unsetCursor()
        self.target.update()

    def mouseRelease(self, event):
        if self.leftButtonPressed:
            self.leftButtonPressed = False
            self.state = FramelessWidget.State.Init
            self.target.update()
            self.activeBorderDragger = None
            self.wholeWidgetDragPos = None

    def updateCursorShape(self, pos):
        if self.target.isFullScreen() or self.target.isMaximized():
            if self.cursorchanged:
                self.target.unsetCursor()
            return

        self.cursorchanged = True
        borderDragger = self.selectActiveBorderDragger(pos)
        if borderDragger is not None:
            self.target.setCursor(borderDragger.getCursorShape())
        else:
            self.target.unsetCursor()

        self.target.update()