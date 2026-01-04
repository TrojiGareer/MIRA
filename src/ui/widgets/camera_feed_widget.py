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

        self._camera_thread : Camera | None = None
        # REMOVED: self._vision = Vision() -> We don't want this on the UI thread!

        self._command_mapper = CommandMapper()

        self.prev_time = 0.0

    def clear(self):
        self.labelCameraFeed.clear()
        self.labelCameraFeed.setText("Camera offline")

    def start_camera(self):
        if not self._camera_thread:
            self._camera_thread = Camera()
            # CHANGED: Connect the new 'frame_processed' signal
            self._camera_thread.frame_processed.connect(self._update_camera_feed)
            self._camera_thread.start()

    def stop_camera(self):
        if self._camera_thread:
            # CHANGED: Disconnect the new signal
            try:
                self._camera_thread.frame_processed.disconnect(self._update_camera_feed)
            except TypeError:
                pass # Handle case where it might already be disconnected
                
            self._camera_thread.stop()
            self._camera_thread = None

        self.clear()

    def _update_camera_feed(self, final_frame: np.ndarray, results: object):
        """
        Now this function is LIGHTWEIGHT. It just draws the image.
        """
        # 1. Forward the results to other widgets (e.g. predictions)
        self.results_processed.emit(results)

        self._command_mapper.process_results(results)

        # 2. Display the image (Convert -> Show)
        pixmap = convert_cv_to_pixmap(final_frame)
        self.labelCameraFeed.setPixmap(pixmap)

        # 3. Update FPS Calculation
        curr_time = time.time()
        elapsed_time = curr_time - self.prev_time
        fps = int(1 / elapsed_time) if elapsed_time > 0 else 0
        self.prev_time = curr_time

        self.fps_signal.emit(fps)