from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit
from PyQt6.QtWidgets import QPushButton, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QStyle, QStyleOption
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion
from PyQt6.QtCore import QRect, QRectF, QSize, QPoint, QEvent

# Hope this will not affect performance much.
class BorderDragger:
    def isActive(self, pos, framerect, borderWidth):
        raise Exception("Not implemented")

    def updateGeometry(self, framerect, pos):
        raise Exception("Not implemented")

    def getCursorShape(self):
        raise Exception("Not implemented")

class CornerDragger(BorderDragger):
    verDragger = BorderDragger()
    horDragger = BorderDragger()

    def isActive(self, pos, framerect, borderWidth):
        return self.verDragger.isActive(pos, framerect, borderWidth) and \
                self.horDragger.isActive(pos, framerect, borderWidth)

    def updateGeometry(self, framerect, pos):
        self.verDragger.updateGeometry(framerect, pos)
        self.horDragger.updateGeometry(framerect, pos)

    def getCursorShape(self):
        raise Exception("Not implemented")

class LeftDragger(BorderDragger):
    def isActive(self, pos, framerect, borderWidth):
        return framerect.contains(pos.toPoint()) and \
                pos.x() >= framerect.x() and \
                pos.x() <= framerect.x() + borderWidth

    def updateGeometry(self, framerect, pos):
        framerect.setLeft(pos.x())

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeHorCursor

class RightDragger(BorderDragger):
    def isActive(self, pos, framerect, borderWidth):
        return framerect.contains(pos.toPoint()) and \
                pos.x() >= framerect.x() + framerect.width() - borderWidth and \
                pos.x() <= framerect.x() + framerect. width()

    def updateGeometry(self, framerect, pos):
        framerect.setRight(pos.x())

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeHorCursor

class TopDragger(BorderDragger):
    def isActive(self, pos, framerect, borderWidth):
        return framerect.contains(pos.toPoint()) and \
                pos.y() >= framerect.y() and \
                pos.y() <= framerect.y() + borderWidth

    def updateGeometry(self, framerect, pos):
        framerect.setTop(pos.y())

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeVerCursor

class BottomDragger(BorderDragger):
    def isActive(self, pos, framerect, borderWidth):
        return framerect.contains(pos.toPoint()) and \
                pos.y() >= framerect.y() + framerect.height() - borderWidth and \
                pos.y() <= framerect.y() + framerect.height()

    def updateGeometry(self, framerect, pos):
        framerect.setBottom(pos.y())

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeVerCursor

class TopLeftDragger(CornerDragger):
    def __init__(self):
        self.verDragger = TopDragger()
        self.horDragger = LeftDragger()

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeFDiagCursor

class TopRightDragger(CornerDragger):
    def __init__(self):
        self.verDragger = TopDragger()
        self.horDragger = RightDragger()

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeBDiagCursor

class BottomLeftDragger(CornerDragger):
    def __init__(self):
        self.verDragger = BottomDragger()
        self.horDragger = LeftDragger()

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeBDiagCursor

class BottomRightDragger(CornerDragger):
    def __init__(self):
        self.verDragger = BottomDragger()
        self.horDragger = RightDragger()

    def getCursorShape(self):
        return QtCore.Qt.CursorShape.SizeFDiagCursor