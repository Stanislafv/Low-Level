from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from base.functions import save
from base.font import Font
from base.cursors import Cursor
from base.MusicPlayer import MusicPlayer
from base.folders import folder

from ui.Menu import Menu

class SettingsMenu(Menu):
    @save
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(Font.Bold)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.fullscreen_check = QtWidgets.QCheckBox("Fullscreen")
        self.fullscreen_check.setCursor(Cursor.Hand)
        self.fullscreen_check.setFont(Font.Bold)
        self.fullscreen_check.clicked.connect(lambda: MusicPlayer.play("click_1"))

        self.music_check = QtWidgets.QCheckBox("Music")
        self.music_check.setFont(Font.Bold)
        self.music_check.setChecked(folder.config["music_volume"] == 0)
        self.music_check.setCursor(Cursor.Hand)
        self.music_check.clicked.connect(lambda: MusicPlayer.play("click_1"))
        
        volume_label = QLabel("Volume:")
        volume_label.setFont(Font.Bold)
        self.volume_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(folder.config["volume"]*100))
        self.volume_slider.setCursor(Cursor.Hand)

        music_volume_label = QLabel("Music Volume:")
        music_volume_label.setFont(Font.Bold)
        self.music_volume_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.music_volume_slider.setRange(0, 100)
        self.music_volume_slider.setValue(int(folder.config["music_volume"]*100))
        self.music_volume_slider.setCursor(Cursor.Hand)
        
        btn_back = QtWidgets.QPushButton("Back")
        btn_back.setFont(Font.Bold)
        btn_back.setCursor(Cursor.Hand)
        btn_back.clicked.connect(lambda: self.Back())
        btn_back.clicked.connect(lambda: MusicPlayer.play("click_1"))
        
        btn_save = QtWidgets.QPushButton("Save")
        btn_save.setFont(Font.Bold)
        btn_save.setCursor(Cursor.Hand)
        btn_save.clicked.connect(lambda: self.save_settings())
        btn_save.clicked.connect(lambda: MusicPlayer.play("click_1"))
        
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
        folder.config.write({"devmode": folder.config["devmode"], "volume": self.volume_slider.value()/100, "music_volume": music_volume})
