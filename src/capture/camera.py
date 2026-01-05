import cv2
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

# Import the Vision class (Relative import since they are in the same folder)
from .vision import Vision

class Camera(QThread):
    # Signal now emits the PROCESSED frame and the RESULTS
    frame_processed = pyqtSignal(np.ndarray, object)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self._camera_index = camera_index
        self._is_running = True
        self._capture = None

    def run(self):
        # 1. Initialize Vision INSIDE the thread
        vision = Vision()
        
        self._capture = cv2.VideoCapture(self._camera_index)
        
        # --- FIX: REMOVE HARDCODED RESOLUTION ---
        # 1280x720 (16:9) often crops the top/bottom of the sensor.
        # By removing these lines, we let the camera use its default (usually 4:3),
        # which gives you the maximum vertical field of view.
        # self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self._capture.isOpened():
            print(f"ERROR: Could not open camera {self._camera_index}")
            return

        print(f"INFO: Camera {self._camera_index} started.")
        self._is_running = True

        while self._is_running and self._capture.isOpened():
            ret, frame = self._capture.read()

            if ret:
                # 2. HEAVY WORK HAPPENS HERE
                processed_frame, results = vision.process_frame(frame)
                
                # 3. Emit the finished work
                self.frame_processed.emit(processed_frame, results)
                
                self.msleep(30) 
            else:
                break
        
        self._capture.release()
        print(f"INFO: Camera stopped.")

    def stop(self):
        self._is_running = False
        self.wait()