from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self.setMinimumSize(800, 600)

        # basic layout
        container = QWidget()
        layout = QVBoxLayout(container)

        # placeholder buttons
        self.btn_train = QPushButton("Open Training Window")
        self.btn_start = QPushButton("Start Camera")
        self.btn_stop = QPushButton("Stop Camera")

        layout.addWidget(self.btn_train)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

        self.setCentralWidget(container)
