import enum
import PyQt6
from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QTextEdit, QSizePolicy, QGridLayout, QMenu, QStyleOption, QStyle, QFileDialog
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QRegion, QIcon, QAction, QPixmap
from PyQt6.QtCore import QRect, QRectF, QLineF, QPointF, QSize, pyqtSlot

import json
import ntpath

from frameless_widget import FramelessWidget

class ConfigureTab(QWidget):
    def __init__(self, viewmodel):
        super().__init__()

        self.state = FramelessWidget.State.Init

        uic.loadUi(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\views\configure_tab.ui', self)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.autoFillBackground()
        self.setWindowFlags(QtCore.Qt.WindowFlags.Window)
        self.setWindowOpacity(1.0)
        self.setWindowFlags(QtCore.Qt.WindowFlags.FramelessWindowHint)
        self.resize(1000, 600)

        self.layout().setSpacing(20)
        self.layout().setVerticalSpacing(20)
        self.layout().setContentsMargins(35, 35, 35, 35)
        self.layout().setColumnStretch(2, 4)
        self.layout().setColumnStretch(3, 8)

        self.previewLayout.setAlignment(self.previewButton, QtCore.Qt.Alignment.AlignVCenter | QtCore.Qt.Alignment.AlignRight)
        self.previewLayout.setAlignment(self.excludeButton, QtCore.Qt.Alignment.AlignVCenter | QtCore.Qt.Alignment.AlignLeft)
        circleButtonSS = """QPushButton {
                                background: rgb(210, 210, 210);
                                border: 0px solid black;
                                border-radius: 25px;
                                font-family: \"Century Gothic\"; /* Text font family */
                                font-size: 10pt; /* Text font size */
                            }
                            QPushButton:hover {
                                background: rgb(144, 200, 246);
                                border-width: 0px;
                                border-radius: 25px;
                                font-family: \"Century Gothic\"; /* Text font family */
                                font-size: 10pt; /* Text font size */
                            }
                            QPushButton:pressed {
                                border-style: solid;
                                border-color: #828282;
                                border-width: 0.5px;
                                border-radius: 25px;
                                font-family: \"Century Gothic\"; /* Text font family */
                                font-size: 10pt; /* Text font size */
                            }"""
        self.previewButton.setStyleSheet(circleButtonSS)
        self.previewButton.setMinimumSize(50, 50)
        self.previewButton.setIcon(QIcon(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\resources\play.png'))
        self.previewButton.setIconSize(PyQt6.QtCore.QSize(50, 50))

        self.excludeButton.setStyleSheet(circleButtonSS)
        self.excludeButton.setMinimumSize(120, 50)
        self.excludeButton.setIcon(QIcon(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\resources\exclude.png'))
        self.excludeButton.setIconSize(PyQt6.QtCore.QSize(40, 40))


        #"background-color: #FAFAFA; /* background color */"
        self.setStyleSheet("""QWidget { border-radius : 5px; }
                              QPushButton {
                                  background: rgb(210, 210, 210);
                                  border: 1px solid black;
                                  border-radius : 0px;
                              }
                              QPushButton:hover {
                                  background: rgb(144, 200, 246);
                                  border-width: 0px;
                                  border-radius : 0px;
                              }
                              QPushButton:pressed {
                                  border-style: solid;
                                  border-color: #828282;
                                  border-width: 1px;
                                  border-radius : 0px;
                              }
                              QLabel {
                                  color: black; /* text color */
                                  border-radius: 5px; }
                              QLabel#cfgActsScript {
                                  font-family: \"Century Gothic\"; /* Text font family */
                                  font-size: 12pt; /* Text font size */}
                              QLabel#actsPicLabel {
                                  border: 1px solid #828282;
                                  border-radius: 5px;
                                  background: white; }
                              QLabel#actsPicPreview {
                                  border: 1px solid #828282;
                                  border-radius: 15px;
                                  background: white }
                              QLabel#actsTimeout {
                                  padding-left: 15px;
                                  padding-right: 15px;
                                  border-radius: 5px; }"""
                           )

        self.actionsList.itemSelectionChanged.connect(self.actionsPicSelectionChanged)

        self.actionsPreviewPixmap = self.actsPicPreview.pixmap()

        self.viewmodel = viewmodel
        self.actionsPictures = []
        self.actionsLabels = []
        self.actionsTimeout = 0

    def browseClicked(self, spinBox, listWidget, mTimeout, mPictures, mLabels):
        config_file_path = QFileDialog.getOpenFileName(self, 'Open file', '/home', '*.json')[0]
        config = None

        if config_file_path == '':
            return
        else:
            listWidget.clear()

        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)

        assert(config)

        timeout = config['timeout']
        spinBox.setValue(timeout)
        mTimeout = timeout

        images = config['images']
        for key, value in images.items():
            mPictures.append(key)
            mLabels.append(value)
            listWidget.addItem(ntpath.basename(key) + ' - ' + value)

    @pyqtSlot(bool)
    def on_browseActions_clicked(self):
        self.browseClicked(self.actionsTimeoutSpinBox, self.actionsList,
                           self.actionsTimeout, self.actionsPictures, self.actionsLabels)

    @pyqtSlot()
    def actionsPicSelectionChanged(self):
        item = self.actionsList.selectedItems()
        row = self.actionsList.row(item[0])
        print("Selected item: ", row)

        self.actsPicLabel.setText(self.actionsLabels[row])
        self.actionsPreviewPixmap = QPixmap(self.actionsPictures[row])
        self.actsPicPreview.setPixmap(self.adjustPixmapToRectSize(self.actionsPreviewPixmap, self.layout().cellRect(2, 2)))

    @pyqtSlot(bool)
    def on_applyButton_clicked(self):
        self.actionsTimeout = self.actionsTimeoutSpinBox.value()
        self.viewmodel.handleApplyButton(self.actionsPictures, self.actionsLabels, self.actionsTimeout)
        self.close()

    @pyqtSlot(bool)
    def on_cancelButton_clicked(self):
        self.close()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(8553090), 0.5)
        brush = QBrush(QColor(15395562))

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(QRectF(rect), 35, 35)
        #it might be needed to clip region for mouse events.
        #painter.setClipPath(path)

        painter.fillPath(path, brush)
        painter.strokePath(path, pen)

        #rect.adjust(12, 12, -12, -12)

        painter.setPen(QPen(QColor(16448251), 4))
        painter.drawLine(QLineF(QPointF(rect.width() / 2 + 13, 75),
                                QPointF(rect.width() / 2 + 13, rect.height() - 45)))

        painter.setPen(QPen(QColor(7697781), 0.5))
        painter.drawLine(QLineF(QPointF(rect.width() / 2 + 13, 75),
                                QPointF(rect.width() / 2 + 13, rect.height() - 45)))

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def resizeEvent(self, event):
        rect = self.layout().cellRect(2, 2)

        self.actsPicPreview.setPixmap(self.adjustPixmapToRectSize(self.actionsPreviewPixmap, rect))

    def adjustPixmapToRectSize(self, pixmap, rect):
        rect.adjust(15, 15, -15, -15)

        if pixmap != None:
            return pixmap.scaled(rect.size(), PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                              PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)

        return None
