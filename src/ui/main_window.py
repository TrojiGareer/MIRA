from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QLabel
from PyQt6.uic.load_ui import loadUiType
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import cv2
import time
import os
from capture import Camera

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, 'main_window.ui')

# The UI is dynamically loaded
try:
    Ui_MainWindow, QtBaseClass = loadUiType(UI_PATH)
except FileNotFoundError:
    print(f"ERROR: UI file not found at {UI_PATH}. Check path and file name.")

    # Use generic QMainWindow if UI file is missing to prevent crash
    class Ui_MainWindow:
        def setupUi(self, MainWindow): pass
    QtBaseClass = QMainWindow


class MainWindow(QtBaseClass, Ui_MainWindow):
    """
    The main application window, inheriting structure from the UI file.
    The LSP can identify the two superclasses of MainWindow as nonexisting but they are created at runtime
    """

    _is_running = False # System state

    # A very sludgy FPS counting system
    _frame_count = 0
    _start_time = 0.0

    def __init__(self):
        super().__init__()
        
        # Use the loaded UI file
        self.setupUi(self)
        
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        
        self._initialize_components()

    def _initialize_components(self):
        """
        Initializes custom logic and connects the UI to the backend(camera, model, etc.)
        """

        # All widgets defined in the .ui file are now attributes of self due to self.setupUi(self)
        # Widgets' names, custom properties are gotten from the .ui files for connecting
        
        # The new widgets added after setuiUi don't take the styles from the .css file => define them here
        self.statusbar.setStyleSheet("""
            background-color: #382437;
            padding: 0px 20px
        """)

        self.camera_thread = None

        # The status bar permanent labels need to be set here

        self.labelFPS = QLabel("FPS: --")
        self.statusbar.addPermanentWidget(self.labelFPS)

        self.labelInterpreterStatus = QLabel("Interpreter: Offline")
        self.statusbar.addPermanentWidget(self.labelInterpreterStatus)

        # Connect signals
        self.buttonStartMIRA.clicked.connect(self.toggle_mira)

        self.statusbar.showMessage("Successfully loaded!", 2000)
        print("INFO: Components initalized successfully!")

    def toggle_mira(self):
        """
        Starts or stops M.I.R.A.
        """

        btn = self.buttonStartMIRA
        
        if not self._is_running:
            self.camera_thread = Camera()
            self.camera_thread.frame_captured.connect(self.update_video_feed)
            self.camera_thread.start()

            self._frame_count = 0
            self._start_time = time.time()

            self._is_running = True
            btn.setText("Stop M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Online") 
            
        else:
            if self.camera_thread:
                # Disconnect the camera to prevent the thread from leaving a last frame
                self.camera_thread.frame_captured.disconnect(self.update_video_feed)
                self.camera_thread.stop()
                self.camera_thread = None

            self.labelVideoFeed.clear()
            self.labelVideoFeed.setText("Camera not active")
            self.labelFPS.setText("FPS: --")

            self._is_running = False
            btn.setText("Start M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Offline")

    def convert_cv_to_pixmap(self, frame: np.ndarray) -> QPixmap:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        frame_size = self.frameVideoFeed.size()
        
        scaled_pixmap = pixmap.scaled(
            frame_size.width(), frame_size.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        return scaled_pixmap

    def update_video_feed(self, frame: np.ndarray):
        """
        Slot: Receives the captured frame from the camera thread and updates the video feed label
        """

        pixmap = self.convert_cv_to_pixmap(frame)
        self.labelVideoFeed.setPixmap(pixmap)

        self._frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self._start_time

        # Aim to update the FPS counter ~each second
        if elapsed_time >= 1.0:
            fps = self._frame_count / elapsed_time
            self.labelFPS.setText(f"FPS: {int(round(fps))}")
            self._frame_count = 0
            self._start_time = current_time
