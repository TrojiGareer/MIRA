from PyQt6.QtWidgets import QHBoxLayout, QWidget

from .live_feed import LiveFeed
from .status_panel import StatusPanel

class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.live_feed_widget = LiveFeed()
        self.status_panel_widget = StatusPanel()

        layout = QHBoxLayout(self)
        layout.addWidget(self.live_feed_widget)
        layout.addWidget(self.status_panel_widget)
