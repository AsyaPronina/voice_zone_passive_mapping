from PyQt6.QtCore import QObject, pyqtSignal

class ConfigureViewModel(QObject):
    model = None

    def __init__(self, model):
        super().__init__()
        self.model = model

    def handleApplyButton(self, pictures, labels, timeout):
        self.model.cleanExperiment()
        self.model.setPictures(pictures)
        self.model.setLabels(labels)
        self.model.setTimeout(timeout)

    def handleCancelButton(self):
        self.model.cleanExperiment()

