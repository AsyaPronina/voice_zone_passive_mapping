import enum
import PyQt6
from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QWidget, QStyleOption, QStyle, QFileDialog
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QIcon, QPixmap, QFont
from PyQt6.QtCore import QRectF, QPointF, pyqtSlot

import json
import ntpath

class ConfigureTab(QWidget):
    def __init__(self, viewmodel, index=0, settingName="Actions"):
        super().__init__()

        self.index = index
        self.settingName = settingName

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

        self.cfgScriptLabel.setText("Configure " + self.settingName + " script")

        self.previewLayout.setAlignment(self.previewButton, QtCore.Qt.Alignment.AlignVCenter | QtCore.Qt.Alignment.AlignRight)
        self.previewLayout.setAlignment(self.nextButton, QtCore.Qt.Alignment.AlignCenter)
        self.previewLayout.setAlignment(self.excludeButton, QtCore.Qt.Alignment.AlignVCenter | QtCore.Qt.Alignment.AlignLeft)
        self.previewLayout.setSpacing(7)
        self.previewLayout.setStretch(0, 9)
        self.previewLayout.setStretch(1, 0)
        self.previewLayout.setStretch(2, 9)
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

        self.nextButton.setStyleSheet(circleButtonSS)
        self.nextButton.setMinimumSize(50, 50)
        self.nextButton.setIcon(QIcon(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\resources\next.png'))
        self.nextButton.setIconSize(PyQt6.QtCore.QSize(50, 50))

        self.excludeButton.setStyleSheet(circleButtonSS)
        self.excludeButton.setMinimumSize(120, 50)
        self.excludeButton.setIcon(QIcon(r'C:\Users\apronina\Syncplicity\Science\Markov_for_passive_ECC_of_voice_zones\voice_zone_passive_mapping\resources\exclude.png'))
        self.excludeButton.setIconSize(PyQt6.QtCore.QSize(40, 40))

        #"background-color: #FAFAFA; /* background color */"
        self.setStyleSheet("""QWidget { border-radius : 5px; }
                              QPushButton {
                                  background: rgb(210, 210, 210);
                                  border: 1px solid #828282;
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
                                  border-radius: 5px;
                              }
                              QLabel#cfgScriptLabel {
                                  font-family: \"Century Gothic\"; /* Text font family */
                                  font-size: 14pt; /* Text font size */
                                  padding: 25px;
                              }
                              QLabel#pictureLabel {
                                  border: 1px solid #828282;
                                  border-radius: 5px;
                                  background: white;
                              }
                              QLabel#picturePreview {
                                  border: 1px solid #828282;
                                  border-radius: 15px;
                                  background: white
                              }
                              QLabel#timeoutLabel {
                                  padding-left: 15px;
                                  padding-right: 15px;
                                  border-radius: 5px;
                              }
                              """
                           )

        self.browseButton.setMinimumSize(50, 23)

        self.picturesListWidget.itemSelectionChanged.connect(self.pictureSelectionChanged)

        self.previewPixmap = self.picturePreview.pixmap()

        self.viewmodel = viewmodel
        self.picturePaths = []
        self.pictureClasses = []
        self.timeoutValue = 0

    @pyqtSlot(bool)
    def on_browseButton_clicked(self):
        config_file_path = QFileDialog.getOpenFileName(self, 'Open file', '/home', '*.json')[0]
        config = None

        if config_file_path == '':
            return
        else:
            self.picturesListWidget.clear()

        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)

        assert(config)

        timeout = config['timeout']
        self.timeoutSpinBox.setValue(timeout)
        self.timeoutValue = timeout

        images = config['images']
        for key, value in images.items():
            self.picturePaths.append(key)
            self.pictureClasses.append(value)
            self.picturesListWidget.addItem(ntpath.basename(key) + ' - ' + value)

    @pyqtSlot()
    def pictureSelectionChanged(self):
        item = self.picturesListWidget.selectedItems()
        row = self.picturesListWidget.row(item[0])
        print("Selected item: ", row)

        self.pictureLabel.setText(self.pictureClasses[row])
        self.previewPixmap = QPixmap(self.picturePaths[row])
        self.picturePreview.setPixmap(self.adjustPixmapToRectSize(self.previewPixmap, self.layout().cellRect(2, 2)))

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHints.Antialiasing)

        pen = QPen(QColor(8553090), 0.5)
        #pen = QPen(QColor(8553090), 1)
        #pen = QPen(QColor(0), 0.5)
        brush = QBrush(QColor(15395562))

        path = QPainterPath()
        rect = QRectF(self.rect())
        rect.adjust(2, 30, -2, -2)
        path.addRoundedRect(QRectF(rect), 35, 35)

        tabPath = QPainterPath()
        tabPath.addRoundedRect(QRectF((self.index * 100) + self.rect().x() + 2, self.rect().y() + 2, 100, 100), 15, 15)
        tabPath.addText(QPointF((self.index * 100) + self.rect().x() + 25, self.rect().y() + 25),
                        QFont("Century Gothic", 10),
                        self.settingName)
        path = path.united(tabPath)
        #it might be needed to clip region for mouse events.
        #painter.setClipPath(path)

        painter.fillPath(path, brush)
        painter.strokePath(path, pen)

        # painter.setPen(QPen(QColor(16448251), 4))
        # painter.drawLine(QLineF(QPointF(rect.width() / 2 + 13, 75),
        #                         QPointF(rect.width() / 2 + 13, rect.height() - 45)))

        # painter.setPen(QPen(QColor(7697781), 0.5))
        # painter.drawLine(QLineF(QPointF(rect.width() / 2 + 13, 75),
        #                         QPointF(rect.width() / 2 + 13, rect.height() - 45)))

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def resizeEvent(self, event):
        rect = self.layout().cellRect(2, 2)

        self.picturePreview.setPixmap(self.adjustPixmapToRectSize(self.previewPixmap, rect))

    def adjustPixmapToRectSize(self, pixmap, rect):
        rect.adjust(15, 15, -15, -15)

        if pixmap != None:
            return pixmap.scaled(rect.size(), PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                              PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)

        return None
