import cv2
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class Camera(QThread):
    """
    QThread worker to capture video frames from the webcam using OpenCV
    Emits the raw numpy array frame for processing and display
    """

    # Signal to emit the captured frame (NumPy array)
    frame_captured = pyqtSignal(np.ndarray)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self._camera_index = camera_index
        self._is_running = True
        self._capture = None

    def run(self):
        """
        The main thread execution loop
        Initializes the camera and reads frames until stopped
        """
        self._capture = cv2.VideoCapture(self._camera_index)
        TARGET_FPS = 20.0
        TARGET_FRAME_TIME = 1000.0 / TARGET_FPS

        if not self._capture.isOpened():
            print(f"ERROR: Could not open camera {self._camera_index}")
            self._is_running = False
            return

        print(f"INFO: Camera {self._camera_index} started.")
        self._is_running = True
        end_loop_time = time.time() * 1000

        while self._is_running and self._capture.isOpened():
            start_loop_time = time.time() * 1000

            ret, frame = self._capture.read()

            if ret:
                # Emit the raw frame data to the main thread (GUI)
                self.frame_captured.emit(frame)
            else:
                print("ERROR: Failed to read frame from camera.")
                break

            end_loop_time = time.time() * 1000
            elapsed_loop_time = end_loop_time - start_loop_time
            # In case the thread runs too fast put it to sleep
            sleep_duration = TARGET_FRAME_TIME - elapsed_loop_time

            if sleep_duration > 1:
                QThread.msleep(int(sleep_duration))
            elif sleep_duration < -10:
                print(f"WARNING: Camera FPS behind target({TARGET_FPS}): {1000.0 / elapsed_loop_time}")

        self._capture.release()
        print(f"INFO: Camera {self._camera_index} stopped and released.")

    def stop(self):
        """Safely stops the thread loop and waits for termination."""
        self._is_running = False
        self.wait() # Wait for the run method to complete its cleanup
