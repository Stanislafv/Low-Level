from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from base.functions import safe_class
from base.folders import folder

from ui.Widgets import Labels, Buttons, Sliders

from ui.Menu import Menu

@safe_class
class SettingsMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title = Labels.Title("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.fullscreen_check = Buttons.Toggle("Fullscreen")

        self.music_check = Buttons.Toggle("Music")
        self.music_check.setChecked(folder.config["music_volume"] == 0)
        
        volume_label = Labels.Body("Volume:")
        self.volume_slider = Sliders.Horizontal()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(folder.config["volume"]*100))

        music_volume_label = Labels.Body("Music Volume:")
        self.music_volume_slider = Sliders.Horizontal()
        self.music_volume_slider.setRange(0, 100)
        self.music_volume_slider.setValue(int(folder.config["music_volume"]*100))
        
        btn_back = Buttons.Secondary("Back")
        btn_back.clicked.connect(lambda: self.Back())
        
        btn_save = Buttons.Secondary("Save")
        btn_save.clicked.connect(lambda: self.save_settings())
        
        layout.addWidget(title)
        layout.addWidget(self.fullscreen_check)
        layout.addWidget(self.music_check)
        layout.addSpacing(5)

        layout.addWidget(volume_label)
        layout.addWidget(self.volume_slider)
        layout.addSpacing(5)

        layout.addWidget(music_volume_label)
        layout.addWidget(self.music_volume_slider)
        layout.addSpacing(20)

        layout.addWidget(btn_save)
        layout.addWidget(btn_back)
        
        self.setFixedSize(300, 400)

    def save_settings(self):
        music_volume = self.music_volume_slider.value()/100 if self.music_check.isChecked() else 0
        folder.config.write({"devmode": folder.config["devmode"], "volume": self.volume_slider.value()/100, "music_volume": music_volume, "craft_coef": folder.config["craft_coef"]})
