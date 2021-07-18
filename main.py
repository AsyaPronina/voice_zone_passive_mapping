import sys
from PyQt6.QtWidgets import QApplication

sys.path.append('views')
from views.doctor_view import DoctorView
from views.menu_bar_view import MenuBarView
from views.records_view import RecordsView
from views.player_view import PlayerView
from views.picture_view import PictureView

from models.experiment_model import ExperimentModel
from viewmodels.menubar_viewmodel import MenuBarViewModel
from viewmodels.records_viewmodel import RecordsViewModel
from viewmodels.player_viewmodel import PlayerViewModel
from viewmodels.picture_viewmodel import PictureViewModel

if __name__ == '__main__':
    app = QApplication(sys.argv)

    model = ExperimentModel()

    menubarView = MenuBarView(MenuBarViewModel(model))
    recordsView = RecordsView(RecordsViewModel(model))
    playerView = PlayerView(PlayerViewModel(model))
    pictureView = PictureView(PictureViewModel(model))
    
    window = DoctorView(menubarView, recordsView, playerView, pictureView)
    window.show()

    sys.exit(app.exec())