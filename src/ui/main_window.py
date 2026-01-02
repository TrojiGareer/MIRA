from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

import numpy as np

import time
from enum import Enum, auto

from capture import Camera, Vision
from ml import Predictor
from ml.train import Recorder, RecordingType

from utils import (
    convert_cv_to_pixmap,
    STATIC_MODEL_PATH,
    STATIC_GESTURE_TRAINING_DATA_PATH
)

from .auto_main_window import Ui_MainWindow


class AppMode(Enum):
    """
    Application modes enum class for M.I.R.A.
    """

    IDLE = auto()
    COLLECTING = auto()
    PREDICTING = auto()

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main application window, inheriting structure from the UI file.
    The LSP can identify the two superclasses of MainWindow as nonexisting but they are created at runtime
    """

    def __init__(self):
        super().__init__()
        
        # UI setup
        self.setupUi(self)
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self._initialize_components()

        self.camera_thread : Camera | None = None
        
        self._vision = Vision()
        self._recorder = Recorder()
        self._predictor = Predictor(STATIC_MODEL_PATH)

        # A very sludgy FPS counting system variables
        self._frame_count = 0
        self._start_time = 0.0

        self._last_prediction_time = 0.0
        self._last_gesture = ""

        self.mode = AppMode.IDLE

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

        # Connect buttons
        self.widgetControlPanel.buttonStartMIRA.clicked.connect(self._toggle_mira)
        self.widgetControlPanel.buttonStartTraining.clicked.connect(self._toggle_data_collection)

        self.statusbar.showMessage("Successfully loaded!", 2000)
        print("INFO: Components initalized successfully!")

    def _clear_all(self):
        """
        Resets the application to the initial state. Clears all the filled data in the UI
        """
        self.widgetPredictions.clear()

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
            self._clear_all()
            self.widgetControlPanel.buttonStartMIRA.setText("Stop M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Online") 
            
        else:
            self._stop_camera()
            self.mode = AppMode.IDLE
            self.widgetControlPanel.buttonStartMIRA.setText("Start M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Offline")

    def _toggle_data_collection(self):
        if not self.mode == AppMode.COLLECTING:
            # if in prediction mode, stop and restart in collection mode
            if self.mode == AppMode.PREDICTING:
                self._toggle_mira()
            self._start_camera()
            self._recorder.reset()
            self.widgetControlPanel.buttonStartTraining.setText("Stop Data Collection")
            self.mode = AppMode.COLLECTING

            self._recorder.pick_recording_type(RecordingType.STATIC)

        else:
            self._stop_camera()
            self.widgetPredictions.clear()
            self.widgetControlPanel.buttonStartTraining.setText("Start Data Collection")
            self.mode = AppMode.IDLE

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
            self.camera_thread = None

        self.widgetCameraFeed.clear()
        self.labelFPS.setText("FPS: --")

    def _process_frame_stream(self, raw_frame: np.ndarray):
        """
        Slot to process each captured frame from the camera thread and send it to the video feed label

        :param raw_frame: The raw captured frame from the camera as a NumPy array
        """

        final_frame, results = self._vision.process_frame(raw_frame)


        if self.mode == AppMode.COLLECTING:
            self._recorder.current_results = results
                
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

        elif self.mode == AppMode.PREDICTING:
            self._predict_and_display(results)

        self.update_fps()

        pixmap = convert_cv_to_pixmap(final_frame)
        self.widgetCameraFeed.labelCameraFeed.setPixmap(pixmap)

    def _predict_and_display(self, results):
        if not results.multi_hand_landmarks:
            self.labelCurrentPrediction.setText("No Hand")
            return

        current_time = time.time()
        if current_time - self._last_prediction_time < 0.5:
            return

        self._last_prediction_time = current_time

        gesture_id = self._predictor.predict(results)
        current_gesture = str(gesture_id)

        self.labelCurrentPrediction.setText(current_gesture)

        if current_gesture != self._last_gesture:
            self.listPredictionLog.addItem(current_gesture)
        
        self._last_gesture = current_gesture

    def keyPressEvent(self, event : QKeyEvent):
        """
        Temporary method for testing data recording from the main window
        """

        print("Key pressed: " + str(event.key()))
        if event.key() == Qt.Key.Key_R and self.mode == AppMode.COLLECTING:
            test_label = "test_gesture"
            self._recorder.save_gesture(test_label, self._recorder.current_results)


    # I mean wtf is ts
    # def keyPressEvent(self, event):
    #     # respond to stage one of data recording, which is label input
    #     if not self.recorder.is_stage_2_recording:
    #         # delete keys if u made a typo
    #         if event.key() == Qt.Key.Key_Backspace:
    #             self.recorder.current_gesture = self.recorder.current_gesture[:-1]
    #             self.labelCurrentPrediction.setText(self.recorder.current_gesture)

    #         # next recording stage
    #         elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
    #             self.recorder.is_stage_2_recording = True
    #             print("Label: " + self.recorder.current_gesture)
    #             self.labelCurrentPredictionText.setText("Recording for ~" + self.recorder.current_gesture + "~")
    #             self.labelCurrentPrediction.setText("Video, static or noise recognition?[v/s/n]")

    #         # print keys as the user types them
    #         elif event.text().isprintable() and event.text():
    #             self.recorder.current_gesture += event.text()
    #             self.labelCurrentPrediction.setText(self.recorder.current_gesture)

    #     # stage 2 scope determination
    #     elif self.recorder.is_stage_2_recording and self.recorder.scope == "unknown":
    #         if event.key() == Qt.Key.Key_V:
    #             self.recorder.scope = "video"
    #         elif event.key() == Qt.Key.Key_S:
    #             self.recorder.scope = "static"
    #         elif event.key() == Qt.Key.Key_N:
    #             self.recorder.scope = "noise"
    #         self.recorder.pick_recording_type()
    #         self.labelCurrentPrediction.setText("Press enter to start recording")

    #     # stage 2
    #     else:
    #         if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
    #             if self.recorder.current_results is None:
    #                 print("no hand on the screen")
    #                 self.labelCurrentPrediction.setText("No hand detected!") 
    #                 return

    #             if self.recorder.scope == "static":
    #                 self.recorder.add_record(self.recorder.current_gesture, self.recorder.current_results)
    #             else:
    #                 # start recording video
    #                 self.recorder.is_recording = True
    #             self.recorder.recordings += 1
    #             self.labelCurrentPrediction.setText(f"Recordings: {self.recorder.recordings}")

    def update_fps(self):
        self._frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self._start_time

        if elapsed_time >= 1.0:
            fps = self._frame_count / elapsed_time
            self.labelFPS.setText(f"FPS: {int(round(fps))}")
            self._frame_count = 0
            self._start_time = current_time