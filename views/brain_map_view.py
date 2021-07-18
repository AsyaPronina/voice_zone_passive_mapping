import PyQt6
from PyQt6 import uic
from PyQt6.QtWidgets import QGridLayout, QWidget, QPushButton, QLabel, QStyle, QStyleOption, QSizePolicy
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QPixmap
from PyQt6.QtCore import QRect, QRectF, QSize, pyqtSlot

class BrainMapView(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\views\brain_map_view.ui', self)
        self.setWindowOpacity(1.0)
        self.setAutoFillBackground(True)
        pal = QPalette(QColor(14079702))
        self.setPalette(pal)

        self.show60_80hz = QPushButton("60-80hz")
        self.show60_80hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show80_100hz = QPushButton("80-100hz")
        self.show80_100hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show100_120hz = QPushButton("100-120hz")
        self.show100_120hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gridLayout.addWidget(self.show60_80hz, 1, 0)
        self.gridLayout.addWidget(self.show80_100hz, 2, 0)
        self.gridLayout.addWidget(self.show100_120hz, 3, 0)
    
        self.showActions = QPushButton('Actions')
        self.showActions.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.showObjects = QPushButton('Objects')
        self.showObjects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gridLayout.addWidget(self.showActions, 0, 1)
        self.gridLayout.addWidget(self.showObjects, 0, 2)

        self.brainMapsGrid = QGridLayout()
        self.gridLayout.addLayout(self.brainMapsGrid, 1, 1, 3, 2)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 8)
        self.gridLayout.setRowStretch(2, 8)
        self.gridLayout.setRowStretch(3, 8)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 9)
        self.gridLayout.setColumnStretch(2, 9)
        
        self.gridLayout.setContentsMargins(10, 3, 10, 3)

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

    # def resizeEvent(self, event):
    #     print(self.rect().size())
    #     self.adjustPixmapToWidgetSize()

    #setScaledContents =  true works much better
    # def adjustPixmapToWidgetSize(self):
    #     rect = self.rect()

    #     #if self.pixmap:
    #         #scaledPixmap = self.pixmap.scaled(rect.size(), PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio, PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
    #         #self.stubLabel.setPixmap(scaledPixmap)
    #     self.brainMapsGrid.setGeometry(rect)