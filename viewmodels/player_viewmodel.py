from PyQt6.QtCore import QObject, pyqtSignal

class PlayerViewModel(QObject):
    model = None

    playing = pyqtSignal(name='playing')
    paused = pyqtSignal(name='paused')
    endOfStream = pyqtSignal(name='endOfStream')

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.playing.connect(self.playing)
        self.model.paused.connect(self.paused)
        self.model.endOfStream.connect(self.endOfStream)

    def handleActionsButton(self):
        pass

    def handleObjectsButton(self):
        pass

    def handlePlayButton(self):
        print("handled play button")
        self.model.playScript()

    def handlePauseButton(self):
        print("handled pause button")
        self.model.pauseScript()

    def handleInvalidateButton(self):
        print("handled invalidate button")
        self.model.moveToNextPicture()

    def handleStopButton(self):
        print("handled stop button")
        self.model.stopScript()