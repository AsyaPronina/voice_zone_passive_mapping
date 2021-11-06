import sys
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, QThread
from threading import Thread
import enum
import time

# InitState -> pyqtSignal INIT to unblock all buttons in all views.
# timeoutUpdated as a stub for now
class PreviewModel(QObject):
    class State(enum.Enum):
        Init = 0
        Paused = 1
        Playing = 2

    state = State.Init

    pictures = []
    labels = []

    activePicturePath = None
    activePictureLabel = None
    playedPictures = 0

    timer = QTimer()
    timeout = 0

    timeoutUpdated = pyqtSignal(name='timeoutUpdated')
    paused = pyqtSignal(name='paused')
    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    endOfStream = pyqtSignal(name='endOfStream')
    previewCleaned = pyqtSignal(name='previewCleaned')

    def __init__(self):
        super().__init__()
        self.__setDefaultTimerInterval()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__playNextPicture)

    def setPictures(self, pictures):
        self.pictures = pictures

    def setLabels(self, labels):
        self.labels = labels

    def setTimeout(self, timeout):
        self.timeout = timeout
        self.timeoutUpdated.emit()

    def getActivePicturePath(self):
        return self.activePicturePath

    def getActivePictureLabel(self):
        return self.activePictureLabel

    def getTimeout(self):
        return self.timeout

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
        self.activePictureLabel = None

        self.endOfStream.emit()
        self.state = PreviewModel.State.Init

    def cleanPreview(self):
        self.stopScript()
        self.previewCleaned.emit()

    def moveToNextPicture(self):
        if self.state != PreviewModel.State.Init:
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

    def __setDefaultTimerInterval(self):
        self.timer.setInterval(self.timeout * 1000)

    def __updateActivePicture(self):
        self.activePicturePath = self.pictures[self.playedPictures]
        self.activePictureLabel = self.labels[self.playedPictures]

    def __playCurrentPicture(self):
        self.timer.start()

    @pyqtSlot()
    def __playNextPicture(self):
        if self.playedPictures < len(self.pictures):
            self.moveToNextPicture()
            self.timer.start()
        else:
            self.stopScript()