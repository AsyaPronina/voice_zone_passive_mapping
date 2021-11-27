from PyQt5.QtCore import QObject, pyqtSignal

class PictureViewModel(QObject):
    model = None

    timeoutUpdated = pyqtSignal(name='timeoutUpdated')
    paused = pyqtSignal(name='paused')
    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    endOfStream = pyqtSignal(name='endOfStream')

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.timeoutUpdated.connect(self.timeoutUpdated)
        self.model.paused.connect(self.paused)
        self.model.playing.connect(self.playing)
        self.model.nextPicture.connect(self.nextPicture)
        self.model.endOfStream.connect(self.endOfStream)

    def picturePath(self):
        return self.model.getActivePicturePath()

    def timeout(self):
        return self.model.getTimeout()