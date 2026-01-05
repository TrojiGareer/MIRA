import time
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from capture import Camera 
# Note: We NO LONGER import Vision here, because Camera handles it!
from utils import convert_cv_to_pixmap
from .auto_camera_feed_widget import Ui_widgetCameraFeed
from commands.mapper import CommandMapper

class CameraFeedWidget(QWidget, Ui_widgetCameraFeed):
    results_processed = pyqtSignal(object) 
    fps_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.labelCameraFeed.setScaledContents(True)

        self._camera_thread : Camera | None = None

        self._command_mapper = CommandMapper()

        self.prev_time = 0.0

    def clear(self):
        self.labelCameraFeed.clear()
        self.labelCameraFeed.setText("Camera offline")

    def start_camera(self):
        if not self._camera_thread:
            self._camera_thread = Camera()
            self._camera_thread.frame_captured.connect(self._update_camera_feed)
            self._camera_thread.start()

    def stop_camera(self):
        if self._camera_thread:
            try:
                self._camera_thread.frame_captured.disconnect(self._update_camera_feed)
            except TypeError:
                pass
                
            self._camera_thread.stop()
            self._camera_thread = None

        self.clear()

    def _update_camera_feed(self, final_frame: np.ndarray, results: object):
        """
        Now this function is LIGHTWEIGHT. It just draws the image.
        """
        self.results_processed.emit(results)

        self._command_mapper.process_results(results)

        pixmap = convert_cv_to_pixmap(final_frame)
        self.labelCameraFeed.setPixmap(pixmap)

        curr_time = time.time()
        elapsed_time = curr_time - self.prev_time
        fps = int(1 / elapsed_time) if elapsed_time > 0 else 0
        self.prev_time = curr_time

        self.fps_signal.emit(fps)
