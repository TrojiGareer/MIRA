import time

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

import numpy as np

from capture import Camera, Vision
from utils import convert_cv_to_pixmap

from .auto_camera_feed_widget import Ui_widgetCameraFeed

class CameraFeedWidget(QWidget, Ui_widgetCameraFeed):
    results_processed = pyqtSignal(object) # Emits the mediapipe processed results
    fps_signal = pyqtSignal(int) # Emits the current FPS value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._camera_thread : Camera | None = None
        self._vision = Vision()

        self.prev_time = 0.0 # Previous time for a frame processed
    
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
            self._camera_thread.frame_captured.disconnect(self._update_camera_feed)
            self._camera_thread.stop()
            self._camera_thread = None

        self.clear()

    def _update_camera_feed(self, raw_frame: np.ndarray):
        """
        Slot to process each captured frame from the camera thread and send it to the video feed label.
        Emits the hand landmark results and FPS via signals

        :param raw_frame: The raw captured frame from the camera as a NumPy array
        """

        final_frame, results = self._vision.process_frame(raw_frame)
        self.results_processed.emit(results)

        pixmap = convert_cv_to_pixmap(final_frame)
        self.labelCameraFeed.setPixmap(pixmap)

        # Update FPS
        curr_time = time.time()
        elapsed_time = curr_time - self.prev_time
        fps = int(1 / elapsed_time) if elapsed_time > 0 else 0
        self.prev_time = curr_time

        self.fps_signal.emit(fps)
