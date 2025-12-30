from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.uic.load_ui import loadUiType
from PyQt6.QtCore import Qt

import numpy as np

import time
from enum import Enum, auto

from capture import Camera
from capture import Vision
from ml import Predictor
from ml import Classifier
from ml.train import Recorder

from utils import (
    convert_cv_to_pixmap,
    UI_FILE_PATH,
    STATIC_MODEL_PATH
)


class AppMode(Enum):
    """
    Application modes enum class for M.I.R.A.
    """

    IDLE = auto()
    COLLECTING = auto()
    PREDICTING = auto()

# The UI is dynamically loaded
try:
    Ui_MainWindow, QtBaseClass = loadUiType(UI_FILE_PATH)
except FileNotFoundError:
    print(f"ERROR: UI file not found at {UI_FILE_PATH}. Check path and file name.")

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
        
        # UI setup
        self.setupUi(self)
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self._initialize_components()

        self.camera_thread = None
        self.vision = Vision()
        self.classifier = Classifier()
        self.recorder = Recorder()
        self.predictor = Predictor(STATIC_MODEL_PATH)

    def _initialize_components(self):
        """
        Private helper that initializes custom UI logic and connects the UI to the backend(camera, model, etc.)
        """

        # All widgets defined in the .ui file are now attributes of self due to self.setupUi(self)
        # Widgets' names, custom properties are gotten from the .ui files for connections


        # The new widgets added after setupUi don't take the styles from the .css file => define them here
        self.statusbar.setStyleSheet("""
            background-color: #382437;
            padding: 0px 20px
        """)

        # Status bar permanent labels
        self.labelFPS = QLabel("FPS: --")
        self.statusbar.addPermanentWidget(self.labelFPS)
        self.labelInterpreterStatus = QLabel("Interpreter: Offline")
        self.statusbar.addPermanentWidget(self.labelInterpreterStatus)

        # Connect signals
        self.buttonStartMIRA.clicked.connect(self._toggle_mira)
        self.buttonStartTraining.clicked.connect(self._toggle_data_collection)

        self.statusbar.showMessage("Successfully loaded!", 2000)
        print("INFO: Components initalized successfully!")

    def _toggle_mira(self):
        """
        Toggles the inference mode of M.I.R.A.
        """

        if not self.mode == AppMode.PREDICTING:
            # if in data collection mode, stop and restart
            if self.mode == AppMode.COLLECTING:
                self._toggle_data_collection()

            self._start_camera()
            self.mode = AppMode.PREDICTING
            self.buttonStartMIRA.setText("Stop M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Online") 
            
        else:
            self.stop_camera()
            self.mode = AppMode.IDLE
            self.buttonStartMIRA.setText("Start M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Offline")
            self.listPredictionLog.clear()

    def _toggle_data_collection(self):
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

    def _start_camera(self):
        if not self.camera_thread:
            self.camera_thread = Camera()
            self.camera_thread.frame_captured.connect(self._process_frame_stream)
            self.camera_thread.start()
            self._start_time = time.time()
            self._frame_count = 0

    def _stop_camera(self):
        if self.camera_thread:
            self.camera_thread.frame_captured.disconnect(self._process_frame_stream)
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        self.labelVideoFeed.clear()
        self.labelVideoFeed.setText("Camera Offline")
        self.labelFPS.setText("FPS: --")
        self.recorder.reset()

    def _process_frame_stream(self, raw_frame: np.ndarray):
        """
        Slot to process each captured frame from the camera thread and send it to the video feed label

        :param raw_frame: The raw captured frame from the camera as a NumPy array
        """

        final_frame, results = self.vision.process_frame(raw_frame)

        # parse all mediapipe frame results to the recorder
        self.recorder.current_results = results

        # custom mode output
        # if self.mode == AppMode.COLLECTING:
        #     # check for live recording
        #     if self.recorder.is_recording:
        #         if self.recorder.session_recording_count < 30:
        #             self.recorder.add_frame_to_current_video(results)
        #             self.recorder.session_recording_count += 1
        #         else:
        #             print(f"recorded {self.recorder.session_recording_count} frames")
        #             self.recorder.is_recording = False
        #             self.recorder.add_video_data()
        #             self.recorder.session_recording_count = 0

        # elif self.mode == AppMode.PREDICTING:
            # self.prediction_mode_display(results)
        self.update_fps()

        pixmap = convert_cv_to_pixmap(final_frame)
        self.labelVideoFeed.setPixmap(pixmap)

    def prediction_mode_display(self, results):
        if not results.multi_hand_landmarks:
            self.labelCurrentPrediction.setText("No Hand")
            self.last_gesture = "No Hand"
            return

        current_time = time.time()
        if current_time - self.last_prediction_time < 0.3:
            self.classifier.past_half_second_frames.append(results)
            return

        self.last_prediction_time = current_time

        # change this line to update the real-time prediction while debugging
        gesture_id = self.predictor.predict(results)
        current_gesture = str(gesture_id) 
        self.classifier.past_half_second_frames = []

        self.labelCurrentPrediction.setText(current_gesture)

        if current_gesture != self.last_gesture:
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
            self.recorder.pick_recording_type()
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