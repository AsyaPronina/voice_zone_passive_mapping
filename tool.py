import sys

sys.path.append('views')
from views.doctor_view import DoctorView
from views.menu_bar_view import MenuBarView
from views.records_view import RecordsView
from views.brain_map_view import BrainMapView
from views.player_view import PlayerView
from views.picture_view import PictureView

from viewmodels.menubar_viewmodel import MenuBarViewModel
from viewmodels.records_viewmodel import RecordsViewModel
from viewmodels.brain_map_viewmodel import BrainMapViewModel
from viewmodels.player_viewmodel import PlayerViewModel
from viewmodels.picture_viewmodel import PictureViewModel

from models.experiment_model import ExperimentModel
from models.tool_config import ToolConfig

from PyQt5.QtWidgets import QApplication

import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    toolConfig = ToolConfig(os.path.join('..', 'configs', 'tool_config.ini'))

    experimentModel = ExperimentModel(toolConfig)

    menubarView = MenuBarView(toolConfig, MenuBarViewModel(experimentModel))
    recordsView = RecordsView(RecordsViewModel(experimentModel))
    brainMapView = BrainMapView(BrainMapViewModel(experimentModel))
    playerView = PlayerView(PlayerViewModel(experimentModel))
    pictureView = PictureView(PictureViewModel(experimentModel))
    
    window = DoctorView(menubarView, recordsView, brainMapView, playerView, pictureView)

    window.show()

    sys.exit(app.exec())