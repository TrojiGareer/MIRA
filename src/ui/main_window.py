from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
)
from PyQt6.QtCore import QSize

from .widgets import HeaderWidget, CentralWidget, FooterWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self.setMinimumSize(QSize(800, 600)) # Increased minimum size for better view

        self._initialize_components()
        self._setup_main_layout()

    """
    Initializes custom component widgets.
    """
    def _initialize_components(self):
        self.header = HeaderWidget()
        self.central_widget = CentralWidget()
        self.footer = FooterWidget()
        
    """
    Arranges the main header, content, and footer.
    """
    def _setup_main_layout(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.central_widget)
        main_layout.addWidget(self.footer)
        
        self.setCentralWidget(main_widget)
