from PyQt6 import uic
from PyQt6.QtWidgets import QListWidgetItem, QPushButton, QTextEdit
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QIcon
from PyQt6.QtCore import QRect, QRectF, QSize, pyqtSlot

class RecordView(QListWidgetItem):
    def __init__(self):
        super().__init__()

        brush = QBrush(QColor(0))
        self.setBackground(brush)

        self.setSizeHint(QSize(50, 50))

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(8553090), 0.5)
        painter.setPen(pen)
        brush = QBrush(QColor(16777215))
        painter.setBrush(brush)

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(rect, 35, 35)

        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

