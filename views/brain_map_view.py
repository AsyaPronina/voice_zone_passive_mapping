import PyQt6
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QGridLayout, QWidget, QPushButton, QLabel, QStyle, QStyleOption, QSizePolicy, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QPointF, pyqtSlot

import numpy as np

class BrainMapView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        uic.loadUi(r'views/brain_map_view.ui', self)
        self.setWindowOpacity(1.0)
        self.setAutoFillBackground(True)
        pal = QPalette(QColor(14079702))
        self.setPalette(pal)

        self.show60_80hz = QPushButton("60-80hz")
        self.show60_80hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show60_80hz.setCheckable(True)
        self.show80_100hz = QPushButton("80-100hz")
        self.show80_100hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show80_100hz.setCheckable(True)
        self.show100_120hz = QPushButton("100-120hz")
        self.show100_120hz.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.show100_120hz.setCheckable(True)
        self.gridLayout.addWidget(self.show60_80hz, 1, 0)
        self.gridLayout.addWidget(self.show80_100hz, 2, 0)
        self.gridLayout.addWidget(self.show100_120hz, 3, 0)
    
        self.showActions = QPushButton('Actions')
        self.showActions.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.showActions.setCheckable(True)
        self.showObjects = QPushButton('Objects')
        self.showObjects.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.showObjects.setCheckable(True)
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

        self.setStyleSheet("""QPushButton {
                                  border: 1px solid #828282;
                                  border-radius : 8px;
                                  font-family: \"IntelOne Display Light\"; /* Text font family */
                                  font-size: 10.5pt; /* Text font size */
                              }
                              QPushButton:hover {
                                  background: rgba(144, 200, 246, 155);
                                  border-color: #828282;
                                  border-width: 1px;
                                  border-radius : 8px;
                                  color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130), stop:1 rgb(32, 47, 130));
                              }
                              QPushButton:pressed,
                              QPushButton:checked
                              {
                                  background: rgba(144, 200, 246, 155);
                                  border-color: #828282;
                                  border-style: solid;
                                  border-width: 1px;
                                  border-radius : 8px;
                                  color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130), stop:1 rgb(32, 47, 130));
                              }
                             """
                           )

        self.show60_80hz.toggled.connect(self.onShow60_80hzStateChanged)
        self.show80_100hz.toggled.connect(self.onShow80_100hzStateChanged)
        self.show100_120hz.toggled.connect(self.onShow100_120hzStateChanged)
        self.showActions.toggled.connect(self.onShowActionsStateChanged)
        self.showObjects.toggled.connect(self.onShowObjectsStateChanged)

        hzs = ["60-80", "80-100", "100-120"]
        picTypes = ["actions", "objects"]

        self.scenes = { (x, y) : QGraphicsScene() for x in hzs for y in picTypes}
        self.scenesWidgets = {}
        self.showHZs = { x : False for x in hzs }
        self.showPicTypes = { x : False for x in picTypes}

        # May be it makes sense to create views anew each time?
        showHZKeys = list(self.showHZs)
        showPicTypesKeys = list(self.showPicTypes) 
        for i in range(0, len(self.showHZs)):
            for j in range(0, len(self.showPicTypes)):
                pair = showHZKeys[i], showPicTypesKeys[j]
                scene = self.scenes[pair]

                for row in range(0, 8):
                    for col in range(0, 8):
                        scene.addRect(QRectF(row * 1000, col * 1000, 1000, 1000))
                        # Transpose view of real matrix??
                        text = scene.addText(str(col * 8 + row + 1), QFont("IntelOne Display Light", 200, 30, True))
                        text.setPos(QPointF(row * 1000, col * 1000))

                scene.setSceneRect(scene.itemsBoundingRect())

                view = QGraphicsView(scene)
                #view.setStyleSheet("background: transparent; border: 0px")
                self.scenesWidgets.update({pair : view})
                self.brainMapsGrid.addWidget(view, i, j)
                view.fitInView(view.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                view.hide()

        self.stateChanged = False

        self.viewmodel = viewmodel
        self.viewmodel.brainMapsUpdated.connect(self.handleBrainMapsUpdated)
        self.viewmodel.experimentCleaned.connect(self.handleExperimentCleaned)

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

        if self.stateChanged:
            for view in self.scenesWidgets.values():
                view.hide()

            for i in range(0, len(self.showHZs)):
                self.brainMapsGrid.setRowStretch(i, 0)

            for j in range(0, len(self.showPicTypes)):
                self.brainMapsGrid.setColumnStretch(j, 0)                    

            onlyHZsToShow = [ x for (x, y) in self.showHZs.items() if y is True ]
            onlyPicTypesToShow = [ x for (x, y) in self.showPicTypes.items() if y is True ]

            for hz in onlyHZsToShow:
                for picType in onlyPicTypesToShow:
                    pair = hz, picType

                    view = self.scenesWidgets[pair]
                    view.show()

                    index = self.brainMapsGrid.indexOf(view)
                    row, col, __, __= self.brainMapsGrid.getItemPosition(index)
                    self.brainMapsGrid.setRowStretch(row, 1)
                    self.brainMapsGrid.setColumnStretch(col, 1)

            self.stateChanged = False

        for hz in self.showHZs:
            for picType in self.showPicTypes:
                pair = hz, picType
                scene = self.scenes[pair]
                view = self.scenesWidgets[pair]
                view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        self.update()

    @pyqtSlot()
    def onShow60_80hzStateChanged(self):
        print("show60_80hz: state changed")
        print(self.show60_80hz.isChecked())

        if self.show60_80hz.isChecked():
            self.showHZs['60-80'] = True
        else:
            self.showHZs['60-80'] = False

        self.stateChanged = True
        self.update()

    @pyqtSlot()
    def onShow80_100hzStateChanged(self):
        print("show80_100hz: state changed")
        print(self.show80_100hz.isChecked())

        if self.show80_100hz.isChecked():
            self.showHZs['80-100'] = True
        else:
            self.showHZs['80-100'] = False

        self.stateChanged = True
        self.update()

    @pyqtSlot()
    def onShow100_120hzStateChanged(self):
        print("show100_120hz: state changed")
        print(self.show100_120hz.isChecked())

        if self.show100_120hz.isChecked():
            self.showHZs['100-120'] = True
        else:
            self.showHZs['100-120'] = False

        self.stateChanged = True
        self.update()

    @pyqtSlot()
    def onShowActionsStateChanged(self):
        print("actions: state changed")
        print(self.showActions.isChecked())

        if self.showActions.isChecked():
            if len([ x for x in self.showHZs.values() if x is True ]) == 0:
                self.show60_80hz.setChecked(True)
            self.showPicTypes['actions'] = True
        else:
            self.showPicTypes['actions'] = False

        self.stateChanged = True
        self.update()

    @pyqtSlot()
    def onShowObjectsStateChanged(self):
        print("objects: state changed")
        print(self.showObjects.isChecked())

        if self.showObjects.isChecked():
            if len([ x for x in self.showHZs.values() if x is True ]) == 0:
                self.show60_80hz.setChecked(True)
            self.showPicTypes['objects'] = True
        else:
            self.showPicTypes['objects'] = False

        self.stateChanged = True
        self.update()

    @pyqtSlot()
    def handleBrainMapsUpdated(self):
        mapsForActions = self.viewmodel.getUpdatedMapsForActions()
        hzs = ['60-80', '80-100', '100-120']
        scenes = []

        for hz in hzs:
            pair = hz, 'actions'
            scene = self.scenes[pair]
            scenes.append(scene)

        colorStart = QColor(32, 47, 130)
        colorEnd = QColor(247, 230, 32)

        for i in range(0, len(scenes)):
            scene = scenes[i]
            map = mapsForActions[i]

            for j in range(0, 8):
                for k in range(0, 8):
                    # map[i, j] should contain values from 0 to 1
                    cvt = lambda x, y, m : (y - x) * m + x
                    r = cvt(colorStart.red(), colorEnd.red(), map[j * 8 + k])
                    g = cvt(colorStart.green(), colorEnd.green(), map[j * 8 + k])
                    b = cvt(colorStart.blue(), colorEnd.blue(), map[j * 8 + k])
                    color = QColor(r, g, b)
                    scene.items(Qt.SortOrder.AscendingOrder)[(k * 8 + j) * 2].setBrush(QBrush(color))

    @pyqtSlot()
    def handleExperimentCleaned(self):
        for hz in self.showHZs:
            for picType in self.showPicTypes:
                pair = hz, picType
                scene = self.scenes[pair]

                for j in range(0, 8):
                    for k in range(0, 8):
                        scene.items(Qt.SortOrder.AscendingOrder)[(k * 8 + j) * 2].setBrush(QBrush(QColor(255, 255, 255)))
