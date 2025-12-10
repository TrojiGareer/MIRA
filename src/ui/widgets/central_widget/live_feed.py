from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout

class LiveFeed(QWidget):
    def __init__(self):
        super().__init__()

        self.lbl_camera = QLabel("Live camera feed:")

        # Layout the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.lbl_camera)
