from PyQt6.QtCore import QObject, pyqtSignal

class RecordsViewModel(QObject):
    model = None

    paused = pyqtSignal(name='paused')
    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    endOfStream = pyqtSignal(name='endOfStream')
    experimentCleaned = pyqtSignal(name='experimentCleaned')

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.paused.connect(self.paused)
        self.model.playing.connect(self.playing)
        self.model.nextPicture.connect(self.nextPicture)
        self.model.endOfStream.connect(self.endOfStream)
        self.model.experimentCleaned.connect(self.experimentCleaned)

    def getActivePictureLabel(self):
        return self.model.getActivePictureLabel()

