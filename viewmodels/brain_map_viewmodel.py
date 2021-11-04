import random

from numpy import matrix

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class BrainMapViewModel(QObject):
    model = None

    brainMapsUpdated = pyqtSignal(name='brainMapsUpdated')
    experimentCleaned = pyqtSignal(name='experimentCleaned')

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.model.nextPicture.connect(self.brainMapsUpdated)
        self.model.endOfStream.connect(self.handleEndOfStream)
        self.model.experimentCleaned.connect(self.experimentCleaned)
        self.coeff = 1
        self.downCoeff = 1

    # Fake maps to emulate "live maps"
    def getUpdatedMapsForActions(self):
        self.coeff = self.coeff + 0.05
        self.downCoeff = self.downCoeff - 0.005

        fakeMap = []
        for i in range(0, 8):
            for j in range(0, 8):
                fakeMap.append(0.1 + random.uniform(0.02, 0.07)) 
        
        for i in range(6, 8):
            for j in range(0, 8):
                fakeMap[i * 8 + j] = 0.15 * self.downCoeff

        for i in range(4, 6):
            for j in range(4, 6):
                fakeMap[i * 8 + j] = 0.13 * self.coeff

        for i in range(6, 8):
            for j in range(6, 8):
                fakeMap[i * 8 + j] = 0.15 * self.coeff

        for i in range(7, 8):
            for j in range(4, 8):
                fakeMap[i * 8 + j] = 0.15 * self.coeff

        return (fakeMap, fakeMap, fakeMap)

    # Empty fake maps
    def getUpdatedMapsForObjects(self):
        fakeMap = None
        return (fakeMap, fakeMap, fakeMap)

    @pyqtSlot()
    def handleEndOfStream(self):
        self.coeff = 1
        self.downCoeff = 1