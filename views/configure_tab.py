import enum
import PyQt5
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle, QFileDialog, QMenu, QAction
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import QRectF, QPointF, pyqtSlot

from resources import resources

import json
import ntpath
import os

from models.tool_config import ToolConfig

from models.tool_config import ToolConfig

class ConfigureTab(QWidget):
    class State(enum.Enum):
        Init = 0
        Paused = 1
        Playing = 2

    def __init__(self, toolConfig, viewmodel, index=0, settingName="Actions"):
        super().__init__()

        self.toolConfig = toolConfig

        self.state = ConfigureTab.State.Init
        self.index = index
        self.settingName = settingName

        uic.loadUi(r'views/configure_tab.ui', self)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.autoFillBackground()
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setWindowOpacity(1.0)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(1000, 600)

        self.layout().setSpacing(20)
        self.layout().setVerticalSpacing(20)
        self.layout().setContentsMargins(35, 35, 35, 35)
        self.layout().setColumnStretch(2, 4)
        self.layout().setColumnStretch(3, 8)

        self.cfgScriptLabel.setText("Configure " + self.settingName + " script")

        self.picturesListWidget.setContextMenuPolicy(PyQt5.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.picturesListWidget.customContextMenuRequested.connect(lambda pos : self.showContextMenu(pos))

        self.buttonsLayout.setAlignment(self.playButton, QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignRight)
        self.buttonsLayout.setAlignment(self.nextButton, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.buttonsLayout.setAlignment(self.excludeButton, QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.buttonsLayout.setSpacing(7)
        self.buttonsLayout.setStretch(0, 9)
        self.buttonsLayout.setStretch(1, 0)
        self.buttonsLayout.setStretch(2, 9)
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
        self.playButton.setStyleSheet(circleButtonSS)
        self.playButton.setMinimumSize(50, 50)
        self.playButton.setIcon(QIcon(r':/logos/play.png'))
        self.playButton.setIconSize(PyQt5.QtCore.QSize(50, 50))

        self.nextButton.setStyleSheet(circleButtonSS)
        self.nextButton.setMinimumSize(50, 50)
        self.nextButton.setIcon(QIcon(r':/logos/next.png'))
        self.nextButton.setIconSize(PyQt5.QtCore.QSize(50, 50))

        self.excludeButton.setStyleSheet(circleButtonSS)
        self.excludeButton.setMinimumSize(120, 50)
        self.excludeButton.setIcon(QIcon(r':/logos/exclude.png'))
        self.excludeButton.setIconSize(PyQt5.QtCore.QSize(40, 40))

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

        self.picturesListWidget.itemClicked.connect(self.pictureSelected)
        self.timeoutSpinBox.valueChanged.connect(self.timeoutSpinBoxValueChanged)

        self.previewPixmap = QPixmap(r':/gui_images/Picture_preview.png')

        self.viewmodel = viewmodel
        self.viewmodel.paused.connect(self.handlePaused)
        self.viewmodel.playing.connect(self.handlePlaying)
        self.viewmodel.nextPicture.connect(self.handleNextPicture)
        self.viewmodel.endOfStream.connect(self.handleEndOfStream)

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

        # update toolConfig pathes
        toolCfgPictures = getattr(self.toolConfig.Stimuli, self.settingName[:-1] + 'Pictures')
        toolCfgPictures.PathToConfig = config_file_path
        self.toolConfig.sync()

        timeout = config['timeout']

        pictures = []
        labels = []
        images = config['images']
        for key, value in images.items():
            pictures.append(str(os.path.abspath(key)))
            labels.append(value)

        self.viewmodel.handleBrowseButton(pictures, labels, timeout)

        pictures = self.viewmodel.getPictures()
        labels = self.viewmodel.getLabels()
        for pic, lab in zip(pictures, labels):
            self.picturesListWidget.addItem(ntpath.basename(pic) + ' - ' + lab)

        self.timeoutSpinBox.setValue(self.viewmodel.getTimeout())

        #
      
    @pyqtSlot()
    def pictureSelected(self):
        row = self.picturesListWidget.currentRow()
        print("Selected item: " + str(row))

        #TODO: doesn't show anything if not played in preview.
        self.viewmodel.handleListItemSelected(row)

    @pyqtSlot()
    def showContextMenu(self, pos):
        globalPos = self.picturesListWidget.mapToGlobal(pos)
        item = self.picturesListWidget.itemAt(pos)
        if not (item.flags() & PyQt5.QtCore.Qt.ItemFlag.ItemIsEnabled):
            print("here")
            menu = QMenu()
            menu.setStyleSheet(
                """QMenu {
                    border-style: solid;
                    border-color: #828282;
                    border-width: 1px;
                }
            }""")
            returnBack = QAction("Return back to script", self)
            returnBack.triggered.connect(lambda: self.returnPictureBack(pos))
            menu.addAction(returnBack)

            menu.exec(globalPos)

    @pyqtSlot()
    def returnPictureBack(self, pos):
        print(self.picturesListWidget.itemAt(pos).text())
        self.viewmodel.handleReturnPictureBackAction(self.picturesListWidget.indexAt(pos).row())
        item = self.picturesListWidget.itemAt(pos)
        item.setFlags(item.flags() | PyQt5.QtCore.Qt.ItemFlag.ItemIsEnabled)

    @pyqtSlot()
    def timeoutSpinBoxValueChanged(self):
        self.viewmodel.handleTimeoutSpinBoxUpdated(self.timeoutSpinBox.value())
        #self.secondsForPicture = self.viewmodel.timeout()

    @pyqtSlot(bool)
    def on_playButton_clicked(self):
        if self.state != ConfigureTab.State.Playing:
            self.viewmodel.handlePlayButton()
        else:
            self.viewmodel.handlePauseButton()

    @pyqtSlot(bool)
    def on_nextButton_clicked(self):
        self.viewmodel.handleNextButton()

    @pyqtSlot(bool)
    def on_excludeButton_clicked(self):
        print("Trying to exclude item: " + str(self.picturesListWidget.currentRow()))
        items = self.picturesListWidget.selectedItems()
        if len(items) > 0:
            item = items[0]
            row = self.picturesListWidget.row(item)
            print("Removing item: ", row)
            self.viewmodel.handleExcludeButton()
            item.setFlags(item.flags() & ~PyQt5.QtCore.Qt.ItemFlag.ItemIsEnabled)
        
    @pyqtSlot()
    def handlePlaying(self):
        print("configure tab: playing")
        self.playButton.setIcon(QIcon(r':/logos/pause.png'))
        #self.perSecTimer.start()
        self.state = ConfigureTab.State.Playing

    @pyqtSlot()
    def handleNextPicture(self):
        print('configure tab: Next picture')

        self.pictureLabel.setText(self.viewmodel.getActiveLabel())
        self.previewPixmap = QPixmap(self.viewmodel.getActivePicture())
        self.picturePreview.setPixmap(self.adjustPixmapToRectSize(self.previewPixmap, self.layout().cellRect(2, 2)))

        self.picturesListWidget.setCurrentRow(self.viewmodel.getActiveListItem())

        # self.secondsForPicture = self.viewmodel.timeout()
        # self.updateTimerLabel(self.secondsForPicture)

        # assert(self.state == ConfigureTab.State.Playing or self.state == ConfigureTab.State.Paused)
        # if self.state == ConfigureTab.State.Playing:
        #     self.perSecTimer.start()
        # else:
        #     # we need to count seconds anew for new picture if state is paused and timer has part of second
        #     if self.perSecTimer.isSingleShot():
        #         #logic repeats handleSecondPassed --> needs to retrieve to one place.
        #         self.perSecTimer.setInterval(self.interval)
        #         self.perSecTimer.setSingleShot(False)

    @pyqtSlot()
    def handlePaused(self):
        print("configure tab: pause")
        self.playButton.setIcon(QIcon(r':/logos/play.png'))
        
        # interval = self.perSecTimer.remainingTime()
        # self.perSecTimer.setInterval(interval)
        # self.perSecTimer.setSingleShot(True)
        # self.perSecTimer.stop()
        self.state = ConfigureTab.State.Paused

    @pyqtSlot()
    def handleEndOfStream(self):
        print('configure tab: no pictures left, end of stream')
        self.playButton.setIcon(QIcon(r':/logos/play.png'))
        self.state = ConfigureTab.State.Init
        #self.secondsForPicture = self.viewmodel.timeout()
        #self.updateTimerLabel(0)
        #self.perSecTimer.stop()

        # self.pixmap = QPixmap()
        # self.pictureLabel.setPixmap(self.pixmap)

        self.state = ConfigureTab.State.Init

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

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

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def resizeEvent(self, event):
        rect = self.layout().cellRect(2, 2)

        pixmap = self.adjustPixmapToRectSize(self.previewPixmap, rect)
        if pixmap:
            self.picturePreview.setPixmap(pixmap)

    def adjustPixmapToRectSize(self, pixmap, rect):
        rect.adjust(15, 15, -15, -15)

        if pixmap:
            return pixmap.scaled(rect.size(), PyQt5.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                              PyQt5.QtCore.Qt.TransformationMode.SmoothTransformation)

        return None
