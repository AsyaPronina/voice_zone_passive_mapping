from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from resources import resources


import sys

sys.path.append('models/recording_model')
from models.recording_model.recording_model import RecordingModel
sys.path.append('models/sc_mapping_model')
from models.sc_mapping_model.sc_mapping_model import SCMappingModel

import enum

# InitState -> pyqtSignal INIT to unblock all buttons in all views.
# timeoutUpdated as a stub for now
class ExperimentModel(QObject):
    class State(enum.Enum):
        Init = 0
        Paused = 1
        Playing = 2

    state = State.Init

    pictures = [r':/test_images/new_running_man.jpg', \
                r':/test_images/sitting_man.png', \
                r':/test_images/mem0.jpg', \
                r':/test_images/mem1.jpg', \
                r':/test_images/mem2.jpg']
    labels = ['label1', 'label2', 'label3', 'label4', 'label5']
    activePicturePath = None
    activePictureLabel = None
    playedPictures = 0

    timer = QTimer()
    timeout = 10

    timeoutUpdated = pyqtSignal(name='timeoutUpdated')
    paused = pyqtSignal(name='paused')
    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    endOfStream = pyqtSignal(name='endOfStream')
    experimentCleaned = pyqtSignal(name='experimentCleaned')

    def __init__(self, toolConfig):
        super().__init__()

        self.toolConfig = toolConfig

        self.__setDefaultTimerInterval()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__playNextPicture)

        self.recordingModel = None
        self.scMappingModel = None

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
        assert(self.state != ExperimentModel.State.Playing)
        self.playing.emit()

        # Now we depend on state in __playNextPicture.
        # Needs refactoring!! 
        if self.state == ExperimentModel.State.Init:
            self.state = ExperimentModel.State.Playing
            self.__playNextPicture()
            # Start patient display model. (It should work via bluetooth client)
            # Activate Display if not debugging or if debugging with stream from LSL_Generator
            # if toolConfig.Mode == ToolConfig.Mode.Debug or toolConfig.LSLOutletRandom:
                # patient_display = Display(config, qs)
                # patient_display.start()
            # Ensure somehow that patient display is started successfully.

            # Create and start recording model and track recorder thread as decoder thread depends on it!
                # recorder = Recorder(config, qs)
                # recorder.record()
                # recorder.start()

            self.recordingModel = RecordingModel(self.toolConfig)

            # Create and start mapping model in a parallel thread.
            self.scMappingModel = SCMappingModel(self.toolConfig)
            self.scMappingModel.set_input_queue(self.recordingModel.get_output_queue())
            self.scMappingModel.start()

        elif self.state == ExperimentModel.State.Paused:
            self.state = ExperimentModel.State.Playing
            self.__playCurrentPicture()

    def pauseScript(self):
        print(self.timer.remainingTime())

        interval = self.timer.remainingTime()
        self.timer.stop()
        self.timer.setInterval(interval)

        self.paused.emit()
        self.state = ExperimentModel.State.Paused

    def stopScript(self):
        self.timer.stop()
        self.__setDefaultTimerInterval()

        self.playedPictures = 0
        self.activePicturePath = None
        self.activePictureLabel = None

        self.endOfStream.emit()
        self.state = ExperimentModel.State.Init

        #if (self.recordingModel.thread.is_alive()):
        #   self.recordingModel.thread.join()
        if self.scMappingModel:
            self.scMappingModel.stop()

    def cleanExperiment(self):
        self.stopScript()
        self.experimentCleaned.emit()

    def moveToNextPicture(self):
        if self.state != ExperimentModel.State.Init:
            # Either we pause script or not, if we are moving to new picture, we should start with new timeout.
            # Refactor if-else logic!! It repeats logic in "__playNextPicture"!
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