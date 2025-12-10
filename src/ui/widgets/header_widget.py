from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)

class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.lbl_title = QLabel("M.I.R.A. Dashboard")
        
        self.btn_settings = QPushButton("Settings")
        # self.btn_settings.setFixedWidth(120)
        
        # Layout the widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.lbl_title)
        layout.addStretch(1)
        layout.addWidget(self.btn_settings)
