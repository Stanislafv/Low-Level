from PyQt6 import QtWidgets
import time

from world.SectorManager import SectorManager

from ui.GameWindow import GameWindow

class EditorWindow(GameWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        save_btn = QtWidgets.QPushButton("Save")
        label = QtWidgets.QLabel("Sector name:")
        entry = QtWidgets.QLineEdit()
        entry.setText("None")
        load_btn = QtWidgets.QPushButton("Load")

        load_btn.clicked.connect(lambda: SectorManager.load_editor(self, entry.text()))

        save_btn.clicked.connect(lambda: SectorManager.save_editor(self, entry.text()))

        layout = QtWidgets.QVBoxLayout()

        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addWidget(label)
        layout.addWidget(entry)
        layout.addWidget(load_btn)
        layout.addStretch()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedWidth(200)

        self.layout().addWidget(widget)

    def show(self):
        self.MainWindow.widget.setCurrentIndex(2)

    def game_tick(self):
        self.now = time.time()
        dt = self.now - self.last_time 
        self.last_time = self.now
        self.update_cam(dt)

