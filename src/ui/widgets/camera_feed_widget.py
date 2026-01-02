from PyQt6.QtWidgets import QWidget
from .auto_camera_feed_widget import Ui_widgetCameraFeed

class CameraFeedWidget(QWidget, Ui_widgetCameraFeed):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
    
    def clear(self):
        self.labelCameraFeed.clear()
        self.labelCameraFeed.setText("Camera offline")
