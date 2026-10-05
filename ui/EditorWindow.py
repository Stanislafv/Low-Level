from PyQt6 import QtWidgets
import time

from base.MusicPlayer import MusicPlayer

from base.functions import safe_class

from ui.GameWindow import GameWindow
from world.WorldEditorLoader import WorldEditorLoader

@safe_class
class EditorWindow(GameWindow):
    def __init__(self, *args, loader=WorldEditorLoader, **kwargs):
        super().__init__(*args, loader=loader, **kwargs)
        save_btn = QtWidgets.QPushButton("Save")
        entry = QtWidgets.QLineEdit()
        entry.setPlaceholderText("Type sector name...")
        load_btn = QtWidgets.QPushButton("Load")

        load_btn.clicked.connect(lambda: self.manager.load(entry.text()))
        save_btn.clicked.connect(lambda: self.manager.save(entry.text()))

        layout = QtWidgets.QVBoxLayout()

        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addWidget(entry)
        layout.addWidget(load_btn)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedWidth(200)

        self.layout().addWidget(widget)

    def show(self):
        self.main_window.widget.setCurrentIndex(2)
        self.timer.start()
        MusicPlayer.start()

    def update(self):
        self.now = time.time()
        dt = self.now - self.last_time 
        self.last_time = self.now
        self.update_cam(dt)

