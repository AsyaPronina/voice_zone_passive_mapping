import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGridLayout, QSizePolicy
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor
from PyQt5.QtCore import QRectF, QSize

from frameless_widget import FramelessWidget

# ui or qss?
# seems that qss should be used

from records_view import RecordsView
from brain_map_view import BrainMapView

class DoctorView(FramelessWidget):
    def __init__(self, menuBarView, recordsView, brainMapView, playerView, pictureView):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        self.state = FramelessWidget.State.Init

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setWindowOpacity(1.0)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setBorderMargin(5)
        self.setCornerMargin(20)
        self.resize(600, 400)

        layout.setSpacing(20)
        layout.setVerticalSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        menuBarView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(menuBarView, 0, 0, 1, 2)

        layout.setRowStretch(0, 0)

        # Seems that it is easier to create custom menu bar with one "Configure experiment" button

        # Fix going to picture limits (picture view limits)!!
        # !!!!!!!!!!!!!!!!!!!!! FIX Fix that each view handles "setMinimumSize" itself.
        # I think setMinimumSize should be handled here.
        recordsView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # QtCore.Qt.AlignmentFlag.AlignCenter) ?
        recordsView.setMinimumSize(QSize(300, 200))
        layout.addWidget(recordsView, 1, 0)

        brainMapView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        brainMapView.setMinimumSize(QSize(300, 200))
        layout.addWidget(brainMapView, 2, 0)

        layout.setRowStretch(1, 4)
        layout.setColumnStretch(0, 4)

        playerView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        playerView.setMinimumSize(QSize(300, 200))
        layout.addWidget(playerView, 1, 1)

        playerView.invalidateLastRecord.connect(recordsView.handleInvalidateLastRecord)

        pictureView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        pictureView.setMinimumSize(QSize(300, 200))
        layout.addWidget(pictureView, 2, 1)

        layout.setRowStretch(2, 6)
        layout.setColumnStretch(1, 3)

        # rect = self.rect().marginsRemoved(QMargins(20, 20, 20, 20))
        # self.layout().setGeometry(rect)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.WheelFocus)        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(8553090), 1)
        cursorShape = self.cursor().shape()
        if cursorShape == QtCore.Qt.CursorShape.SizeHorCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeVerCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeFDiagCursor or \
           cursorShape == QtCore.Qt.CursorShape.SizeBDiagCursor or \
           self.state == FramelessWidget.State.Resizing:
            pen = QPen(QColor(8553000), 5)
        painter.setPen(pen)
        brush = QBrush(QColor(14079702))
        painter.setBrush(brush)

        path = QPainterPath()
        rect = event.rect()
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(QRectF(rect), 35, 35)
        #it might be needed to clip region for mouse events.
        #painter.setClipPath(path)

        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

    def closeEvent(self, event):
        event.accept()
        sys.exit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()