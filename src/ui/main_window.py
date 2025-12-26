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

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # data collecting_mode
        self.is_collecting_data = False
        self.current_raw_landmarks = None
        self.user_input_buffer = ""
        self.is_stage_2_recording = False
        self.session_recording_count = 0

        # predictions integration
        self.listPredictionLog.clear()
        self.last_gesture = "None"
        self.recorder = Recorder('../hand_data.csv')
        self.interpreter = Interpreter('model.p')

        self.listPredictionLog.setFixedWidth(300)
        self.labelCurrentPrediction.setFixedWidth(500)
        self.labelCurrentPrediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonStartMIRA.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonStartTraining.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Connect signals
        self.buttonStartMIRA.clicked.connect(self.toggle_mira)
        self.buttonStartTraining.clicked.connect(self.toggle_data_collection)

        self.statusbar.showMessage("Successfully loaded!", 2000)
        print("INFO: Components initalized successfully!")

    def toggle_data_collection(self):
        """
        Starts the data collection mode
        """

        btn = self.buttonStartTraining
        if not self.is_collecting_data:
            # if the camera was already running, disconnect interpreter
            if self._is_running:
                self.toggle_mira()
            
            # start the camera and load the ui changes needed
            self.camera_thread = Camera()
            self.camera_thread.frame_captured.connect(self.draw_and_show)
            self.camera_thread.start()

            btn.setText("Stop Data Collection")
            self.labelCurrentPredictionText.setText("Label: ")
            self.labelCurrentPrediction.setText("type label to start")
            self.buttonExecutePrediction.setText("Done")
            self.is_collecting_data = True

            # start listening and collecting
            self.setFocus()


        else:
            if self.camera_thread:
                # Disconnect the camera to prevent the thread from leaving a last frame
                self.camera_thread.frame_captured.disconnect(self.draw_and_show)
                self.camera_thread.stop()
                self.camera_thread.wait()
                self.camera_thread = None
            self.labelVideoFeed.clear()
            
            btn.setText("Start Data Collection")
            self.labelVideoFeed.setText("Camera not active")
            self.labelCurrentPredictionText.setText("Current Prediction: ")
            self.labelCurrentPrediction.setText("-")
            self.buttonExecutePrediction.setText("Execute")
            self.is_collecting_data = False
            self.user_input_buffer = ""
            self.is_stage_2_recording = False
            self.session_recording_count = 0

    def draw_and_show(self, frame: np.ndarray):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        self.current_raw_landmarks = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # store and draw the hand landmarks on each frame
                self.current_raw_landmarks = hand_landmarks
    
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        pixmap = self.convert_cv_to_pixmap(frame)
        self.labelVideoFeed.setPixmap(pixmap)

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
                self.camera_thread.wait()
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
        Slot: Receives the captured frame, draws hand landmarks, and updates the display
        """

        # bgr -> rgb
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        current_gesture = "No Hand"

        # draw landmarks if hands are found
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

                # here is where the magic happens
                prediction = self.interpreter.predict(hand_landmarks)
                current_gesture = prediction

        self.labelCurrentPrediction.setText(current_gesture)

        # B. Update the "Log" only if the gesture has CHANGED
        if current_gesture != self.last_gesture:
            if current_gesture != "No Hand":
                self.listPredictionLog.insertItem(0, current_gesture)
                
                if self.listPredictionLog.count() > 10:
                    self.listPredictionLog.takeItem(10)
            
            self.last_gesture = current_gesture

        pixmap = self.convert_cv_to_pixmap(frame)
        self.labelVideoFeed.setPixmap(pixmap)

        # update fps counter
        self._frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self._start_time

        if elapsed_time >= 1.0:
            fps = self._frame_count / elapsed_time
            self.labelFPS.setText(f"FPS: {int(round(fps))}")
            self._frame_count = 0
            self._start_time = current_time

    def keyPressEvent(self, event):
        # respond to stage one of data recording, which is label input
        if not self.is_stage_2_recording:
            # quit if you finished typing and entered or started accidentally
            if event.key() == Qt.Key.Key_Q and self.user_input_buffer == "":
                print("Exited typing mode")
                return

            # delete keys if u made a typo
            if event.key() == Qt.Key.Key_Backspace:
                self.user_input_buffer = self.user_input_buffer[:-1]
                self.labelCurrentPrediction.setText(self.user_input_buffer)

            # reset and print to console on enter for now
            elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                print("Label: " + self.user_input_buffer)
                self.labelCurrentPredictionText.setText("Recording for ~" + self.user_input_buffer + "~")
                self.labelCurrentPrediction.setText("Press enter to record data")
                self.is_stage_2_recording = True

            # print keys as the user types them
            elif event.text().isprintable() and event.text():
                self.user_input_buffer += event.text()
                self.labelCurrentPrediction.setText(self.user_input_buffer)
        else:
            #stage two of the data collection, which is data gathering
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if self.current_raw_landmarks is None:
                    print("no hand on the screen")
                    self.labelCurrentPrediction.setText("No hand detected!") 
                    return

                self.recorder.add_record(self.user_input_buffer, self.current_raw_landmarks)
                self.session_recording_count += 1
                self.labelCurrentPrediction.setText(f"Recordings: {self.session_recording_count}")

    # this is just for debugging and testing
    def print_raw_lm(self, hand_landmarks):
        for i in range(21):
            lm = hand_landmarks.landmark[i]
            
            print(f"Point {i}: x={lm.x}, y={lm.y}")
        
        print("-" * 20)