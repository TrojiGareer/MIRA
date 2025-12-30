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
        self._capture = cv2.VideoCapture(self._camera_index)

        # Try to set HD resolution (1280x720). If camera doesn't support it, it uses closest match.
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self._capture.isOpened():
            print(f"ERROR: Could not open camera {self._camera_index}")
            self._is_running = False
            return

        print(f"INFO: Camera {self._camera_index} started.")
        self._is_running = True

        while self._is_running and self._capture.isOpened():
            # Read frame (This effectively 'sleeps' until hardware has a new frame)
            ret, frame = self._capture.read()

            if ret:
                self.frame_captured.emit(frame)
            else:
                break
                
        self._capture.release()
        print(f"INFO: Camera stopped.")
        
    def stop(self):
        """Safely stops the thread loop and waits for termination."""
        
        self._is_running = False
        self.wait() # Wait for the run method to complete its cleanup
