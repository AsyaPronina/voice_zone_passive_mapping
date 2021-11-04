import enum
import PyQt6
from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QTextEdit, QSizePolicy, QGridLayout, QMenu, QStyleOption, QStyle, QFileDialog
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QIcon, QAction, QPixmap
from PyQt6.QtCore import QRect, QRectF, QLineF, QPointF, QSize, pyqtSlot

import json
import ntpath

from frameless_widget import FramelessWidget
from configure_tab import ConfigureTab

class ConfigureView(FramelessWidget):
    def __init__(self, viewmodel):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)

        self.state = FramelessWidget.State.Init

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.autoFillBackground()
        self.setWindowFlags(QtCore.Qt.WindowFlags.Window)
        self.setWindowOpacity(1.0)
        self.setWindowFlags(QtCore.Qt.WindowFlags.FramelessWindowHint)
        self.setBorderMargin(5)
        self.setCornerMargin(20)
        self.resize(1000, 600)

        # self.actionsViewModel
        # self.objectsViewModel
        tab = ConfigureTab(viewmodel)
        tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # QtCore.Qt.Alignment.AlignCenter) ?
        tab.setMinimumSize(QSize(300, 200))
        self.layout().addWidget(tab)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(8553090), 1)
        cursorShape = self.cursor().shape()
        if cursorShape == QtCore.Qt.CursorShape.SizeHorCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeVerCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeFDiagCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeBDiagCursor or \
           self.state == FramelessWidget.State.Resizing:
           pen = QPen(QColor(8553000), 5)
        brush = QBrush(QColor(14079702))

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(QRectF(rect), 35, 35)
        #it might be needed to clip region for mouse events.
        #painter.setClipPath(path)

        painter.fillPath(path, brush)
        painter.strokePath(path, pen)

        # rect.adjust(12, 12, -12, -12)
        # innerPath = QPainterPath()
        # innerPath.addRoundedRect(QRectF(rect), 35, 35)
        # painter.fillPath(innerPath, QBrush(QColor(15395562)))
        # painter.strokePath(innerPath, QPen(QColor(8553090), 0.5))

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def keyPressEvent(self, event):
        if event.keyCombination().key() == QtCore.Qt.Key.Key_Escape:
            self.close()