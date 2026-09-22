from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from base.font import Font

class ResourcePanel(QtWidgets.QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.w = window
        
        self.layout_ = QtWidgets.QVBoxLayout(self)
        self.labels = {}
        
        self.resource_types = ["coal", "lead"]

        for resource in self.resource_types:
            label = QLabel(f"{resource}: 0")
            label.setFont(Font.Bold)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout_.addWidget(label)
            self.labels[resource] = label
            label.show()
        
        self.setMinimumSize(150, 50)
        self.show()
        self.raise_()

        self.update({})
    
    def update(self, dct):
        for resource, label in self.labels.items():
            if resource in dct:
                label.setText(f"{resource}: {dct[resource]}")
                label.show()
            else:
                label.hide()
        
        self.adjustSize()
        #self.move((self.parent().width() - self.width()) // 2, 0)
