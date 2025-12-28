from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QLabel
from PyQt6.uic.load_ui import loadUiType
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import cv2
import time
import os
from capture import Camera
import mediapipe as mp
import csv
from utils.recorder import Recorder
from interpreter import Interpreter
from utils.vision import Vision
from enum import Enum, auto

class AppMode(Enum):
    IDLE = auto()
    COLLECTING = auto()
    PREDICTING = auto()

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

    _frame_count = 0
    _start_time = 0.0

    def __init__(self):
        super().__init__()
        self.mode = AppMode.IDLE
        
        # ui setup
        self.setupUi(self)
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self.statusbar.setStyleSheet("""
            background-color: #382437;
            padding: 0px 20px
        """)

        # status bar permanent labels
        self.labelFPS = QLabel("FPS: --")
        self.statusbar.addPermanentWidget(self.labelFPS)
        self.labelInterpreterStatus = QLabel("Interpreter: Offline")
        self.statusbar.addPermanentWidget(self.labelInterpreterStatus)

        # predictions integration
        self.last_gesture = "None"

        # custom helper objects
        self.camera_thread = None
        self.vision = Vision()
        self.recorder = Recorder('../static_hand_data.csv', '../video_hand_data.csv', '../noise_hand_data.csv')
        self.interpreter = Interpreter('model.p')

        self.listPredictionLog.setFixedWidth(300)
        self.labelCurrentPrediction.setFixedWidth(500)
        self.labelCurrentPrediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonStartMIRA.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonStartTraining.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # button functionality
        self.buttonStartMIRA.clicked.connect(self.toggle_mira)
        self.buttonStartTraining.clicked.connect(self.toggle_data_collection)

        self.statusbar.showMessage("Successfully loaded!", 2000)
        print("INFO: Components initalized successfully!")

    def toggle_data_collection(self):
        if not self.mode == AppMode.COLLECTING:
            # if in prediction mode, stop and restart in collection mode
            if self.mode == AppMode.PREDICTING:
                self.toggle_mira()
            self.start_camera()
            self.buttonStartTraining.setText("Stop Data Collection")
            self.labelCurrentPredictionText.setText("Label: ")
            self.labelCurrentPrediction.setText("type label to start")
            self.buttonExecutePrediction.setText("Done")
            self.mode = AppMode.COLLECTING

            # start listening and collecting
            self.setFocus()

        else:
            self.stop_camera()            
            self.buttonStartTraining.setText("Start Data Collection")
            self.labelCurrentPredictionText.setText("Current Prediction: ")
            self.labelCurrentPrediction.setText("-")
            self.buttonExecutePrediction.setText("Execute")
            self.mode = AppMode.IDLE
            self.recorder.current_gesture = ""
            self.recorder.is_stage_2_recording = False
            self.recorder.recordings = 0

    def toggle_mira(self):
        if not self.mode == AppMode.PREDICTING:
            # if in data collection mode, stop and restart
            if self.mode == AppMode.COLLECTING:
                self.toggle_data_collection()
            self.start_camera()
            self.mode = AppMode.PREDICTING
            self.buttonStartMIRA.setText("Stop M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Online") 
            
        else:
            self.stop_camera()
            self.mode = AppMode.IDLE
            self.buttonStartMIRA.setText("Start M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Offline")
            self.listPredictionLog.clear()

    # this runs once every frame
    def process_frame_stream(self, raw_frame: np.ndarray):
        final_frame, results = self.vision.process_frame(raw_frame)

        # parse all mediapipe frame results to the recorder
        self.recorder.current_results = results

        # custom mode output
        if self.mode == AppMode.COLLECTING:
            # check for live recording
            if self.recorder.is_recording:
                if self.recorder.session_recording_count < 30:
                    self.recorder.add_frame_to_current_video(results)
                    self.recorder.session_recording_count += 1
                else:
                    print(f"recorded {self.recorder.session_recording_count} frames")
                    self.recorder.is_recording = False
                    self.recorder.add_video_data()
                    self.recorder.session_recording_count = 0

        elif self.mode == AppMode.PREDICTING:
            self.prediction_mode_display(results)
        self.update_fps()

        # actual display part
        w = self.labelVideoFeed.width()
        h = self.labelVideoFeed.height()
        pixmap = self.vision.convert_cv_to_pixmap(final_frame, w, h)
        
        self.labelVideoFeed.setPixmap(pixmap)

    def start_camera(self):
        if not self.camera_thread:
            self.camera_thread = Camera()
            self.camera_thread.frame_captured.connect(self.process_frame_stream)
            self.camera_thread.start()
            self._start_time = time.time()
            self._frame_count = 0

    def stop_camera(self):
        if self.camera_thread:
            self.camera_thread.frame_captured.disconnect(self.process_frame_stream)
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        self.labelVideoFeed.clear()
        self.labelVideoFeed.setText("Camera Offline")
        self.labelFPS.setText("FPS: --")
        self.recorder.reset()

    def prediction_mode_display(self, results):
        current_gesture = "No Hand"

        # put predictions on the screen
        if results.multi_hand_landmarks:
            prediction = self.interpreter.predict(self.recorder.current_results)
            current_gesture = prediction
        else:
            current_gesture = "No Hand"

        self.labelCurrentPrediction.setText(current_gesture)

         # update the log only if the gesture has changed
        if current_gesture != self.last_gesture:
            if current_gesture != "No Hand":
                self.listPredictionLog.insertItem(0, current_gesture)
                    
                if self.listPredictionLog.count() > 10:
                    self.listPredictionLog.takeItem(10)
                
        self.last_gesture = current_gesture

    def keyPressEvent(self, event):
        # respond to stage one of data recording, which is label input
        if not self.recorder.is_stage_2_recording:
            # delete keys if u made a typo
            if event.key() == Qt.Key.Key_Backspace:
                self.recorder.current_gesture = self.recorder.current_gesture[:-1]
                self.labelCurrentPrediction.setText(self.recorder.current_gesture)

            # next recording stage
            elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.recorder.is_stage_2_recording = True
                print("Label: " + self.recorder.current_gesture)
                self.labelCurrentPredictionText.setText("Recording for ~" + self.recorder.current_gesture + "~")
                self.labelCurrentPrediction.setText("Video, static or noise recognition?[v/s/n]")

            # print keys as the user types them
            elif event.text().isprintable() and event.text():
                self.recorder.current_gesture += event.text()
                self.labelCurrentPrediction.setText(self.recorder.current_gesture)

        # stage 2 scope determination
        elif self.recorder.is_stage_2_recording and self.recorder.scope == "unknown":
            if event.key() == Qt.Key.Key_V:
                self.recorder.scope = "video"
            elif event.key() == Qt.Key.Key_S:
                self.recorder.scope = "static"
            elif event.key() == Qt.Key.Key_N:
                self.recorder.scope = "noise"
            self.recorder.pick_data_file()
            self.labelCurrentPrediction.setText("Press enter to start recording")

        # stage 2
        else:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if self.recorder.current_results is None:
                    print("no hand on the screen")
                    self.labelCurrentPrediction.setText("No hand detected!") 
                    return

                if self.recorder.scope == "static":
                    self.recorder.add_record(self.recorder.current_gesture, self.recorder.current_results)
                else:
                    # start recording video
                    self.recorder.is_recording = True
                self.recorder.recordings += 1
                self.labelCurrentPrediction.setText(f"Recordings: {self.recorder.recordings}")

    def update_fps(self):
        self._frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self._start_time

        if elapsed_time >= 1.0:
            fps = self._frame_count / elapsed_time
            self.labelFPS.setText(f"FPS: {int(round(fps))}")
            self._frame_count = 0
            self._start_time = current_time