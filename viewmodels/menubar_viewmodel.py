from PyQt6.QtCore import QObject, pyqtSignal

class MenuBarViewModel(QObject):
    model = None

    def __init__(self, model):
        super().__init__()
        self.model = model

    def getModel(self):
        return self.model

    def stopScript(self):
        return self.model.stopScript()