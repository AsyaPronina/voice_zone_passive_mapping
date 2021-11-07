from PyQt6.QtCore import QObject, pyqtSignal

class ConfigureScriptViewModel(QObject):

    playing = pyqtSignal(name='playing')
    nextPicture = pyqtSignal(name='nextPicture')
    paused = pyqtSignal(name='paused')
    endOfStream = pyqtSignal(name='endOfStream')

    def __init__(self, previewModel, experimentModel):
        super().__init__()

        # FIX THE SAME IN OTHE VIEWMODELS! NO CLASS VARIABLE?
        # The signal should not be shared between each instance
        self.previewModel = previewModel

        self.previewModel.playing.connect(self.playing)
        self.previewModel.nextPicture.connect(self.nextPicture)
        self.previewModel.paused.connect(self.paused)
        self.previewModel.endOfStream.connect(self.endOfStream)

        self.experimentModel = experimentModel

    def getPictures(self):
        return self.previewModel.getPictures()

    def getLabels(self):
        return self.previewModel.getLabels()

    def getTimeout(self):
        return self.previewModel.getTimeout()

    def getActivePicture(self):
        return self.previewModel.getActivePicturePath()

    def getActiveLabel(self):
        return self.previewModel.getActivePictureLabel()

    def getActiveListItem(self):
        return self.previewModel.getActivePictureIndex()

    def cleanPreview(self):
        self.previewModel.cleanPreview()

    def handleBrowseButton(self, pictures, labels, timeout):
        self.previewModel.setPicturesAndLabels(pictures, labels)
        self.previewModel.setTimeout(timeout)

    def handleListItemSelected(self, row):
        self.previewModel.moveToPicture(row)

    def handleTimeoutSpinBoxUpdated(self, timeout):
        self.previewModel.setTimeout(timeout)

    def handlePlayButton(self):
        print("handled play button")
        self.previewModel.playScript()

    def handlePauseButton(self):
        print("handled pause button")
        self.previewModel.pauseScript()

    def handleNextButton(self):
        print("handled next button")
        self.previewModel.moveToNextPicture()

    def handleExcludeButton(self):
        print("handled exclude button")
        self.previewModel.removeCurrentPicture()

    def handleReturnPictureBackAction(self, index):
        print("handled return picture back action")
        self.previewModel.returnPictureBack(index)
