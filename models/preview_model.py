import sys
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, QThread
from threading import Thread
import enum
import time

from sortedcontainers import SortedDict

# InitState -> pyqtSignal INIT to unblock all buttons in all views.
class PreviewModel(QObject):
    class State(enum.Enum):
        Init = 0
        Paused = 1
        Playing = 2

    paused = pyqtSignal(name='paused')
    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    endOfStream = pyqtSignal(name='endOfStream')
    previewCleaned = pyqtSignal(name='previewCleaned')

    def __init__(self):
        super().__init__()

        # FIX THE SAME IN EXPERIMENT MODEL! NO CLASS VARIABLE?
        # The signal should not be shared between each instance
        self.state = PreviewModel.State.Init

        self.pictures = SortedDict()
        self.labels = SortedDict()
        self.excludedPairs = SortedDict()
    
        self.activePicturePath = None
        self.activePictureIndex = None
        self.activePictureLabel = None
        self.playedPictures = 0
    
        self.timer = QTimer()
        self.timeout = 0

        self.__setDefaultTimerInterval()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__playNextPicture)

    def setPicturesAndLabels(self, pictures, labels):
        self.pictures = SortedDict({ i : pictures[i] for i in range(0, len(pictures)) })
        self.labels = SortedDict({ i: labels[i] for i in range(0, len(labels)) })

    def setTimeout(self, timeout):
        self.timeout = timeout

    def getPictures(self):
        pictures = [ value for value in self.pictures.values() ]
        return pictures

    def getLabels(self):
        labels = [ value for value in self.labels.values() ]
        return labels

    def getTimeout(self):
        return self.timeout

    def getActivePicturePath(self):
        return self.activePicturePath

    def getActivePictureIndex(self):
        return self.activePictureIndex

    def getActivePictureLabel(self):
        return self.activePictureLabel

    def playScript(self):
        assert(self.state != PreviewModel.State.Playing)
        self.playing.emit()

        # Now we depend on state in __playNextPicture.
        # Needs refactoring!! 
        if self.state == PreviewModel.State.Init:
            self.state = PreviewModel.State.Playing
            self.__playNextPicture()
        elif self.state == PreviewModel.State.Paused:
            self.state = PreviewModel.State.Playing
            self.__playCurrentPicture()

    def pauseScript(self):
        print(self.timer.remainingTime())

        interval = self.timer.remainingTime()
        self.timer.stop()
        self.timer.setInterval(interval)

        self.paused.emit()
        self.state = PreviewModel.State.Paused

    def stopScript(self):
        self.timer.stop()
        self.__setDefaultTimerInterval()

        self.playedPictures = 0
        self.activePicturePath = None
        # Just to POINT that this index remains the same
        self.activePictureIndex = self.activePictureIndex
        self.activePictureLabel = None

        self.endOfStream.emit()
        self.state = PreviewModel.State.Init

    def cleanPreview(self):
        self.stopScript()
        self.previewCleaned.emit()

    def moveToNextPicture(self):
        print("moveToNextPicture for: " + str(self.playedPictures))
        print("from: " + str(len(self.pictures)))
        # Either we pause script or not, if we are moving to new picture, we should start with new timeout.
        # Refactor if-else logic!! It repeats logic in "__playNextPicture"!
        # REFACTOR!!
        if self.playedPictures < len(self.pictures):
            self.__setDefaultTimerInterval()
            self.__updateActivePicture()
            self.playedPictures += 1
            self.nextPicture.emit()
        else:
            self.stopScript()

    def moveToPicture(self, index):
        print("preview model: move to picture")
        if index in list(self.pictures.keys()):
            self.playedPictures = list(self.pictures.keys()).index(index)
            print("moveToPicture for : " + str(self.playedPictures))
            self.moveToNextPicture()

    def removeCurrentPicture(self):
        index = self.getActivePictureIndex()
        print("preview model: removing " + str(index) + " picture from set")
        self.excludedPairs.update({ index : (self.pictures[index], self.labels[index]) })
        del self.pictures[index]
        del self.labels[index]
        self.playedPictures -= 1

    def returnPictureBack(self, index):
        assert(index in self.excludedPairs.keys())
        picture, label = self.excludedPairs[index]
        self.pictures[index] = picture
        self.labels[index] = label
        del self.excludedPairs[index]

        if self.getActivePictureIndex() > index:
            self.playedPictures += 1

    def __setDefaultTimerInterval(self):
        self.timer.setInterval(self.timeout * 1000)

    def __updateActivePicture(self):
        self.activePictureIndex, self.activePicturePath = list(self.pictures.items())[self.playedPictures]
        self.activePictureLabel = list(self.labels.values())[self.playedPictures]

    def __playCurrentPicture(self):
        self.timer.start()

    @pyqtSlot()
    def __playNextPicture(self):
        print("__playNextPicture: self.playedPictures = " + str(self.playedPictures))
        print("__playNextPicture: len(self.pictures) = " + str(len(self.pictures)))
        if self.playedPictures < len(self.pictures):
            self.moveToNextPicture()
            self.timer.start()
        else:
            self.stopScript()