from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

class FooterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.lbl_status_fps = QLabel("FPS: -- | Webcam: Disconnected")
        self.lbl_status_interpreter = QLabel("Interpreter: DISABLED")

        # Layout the widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.lbl_status_fps)
        layout.addStretch(1)
        layout.addWidget(self.lbl_status_interpreter)
