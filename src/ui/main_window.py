import time
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QAction  # ADDED QAction

from enum import Enum, auto

from .auto_main_window import Ui_MainWindow
from ml.train.recorder import RecordingType

class AppMode(Enum):
    IDLE = auto()
    COLLECTING = auto()
    PREDICTING = auto()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # UI setup
        self.setupUi(self)
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        self._initialize_components()

        self.mode = AppMode.IDLE

    def _initialize_components(self):
        """
        Initializes custom UI logic and connects backend.
        """
        self.statusbar.setStyleSheet("""
            background-color: #382437;
            padding: 0px 20px
        """)

        self.menubar.clear()
        self.action_help = QAction("Help", self)
        self.action_help.triggered.connect(self.widgetPredictions.show_help_dialog)
        self.menubar.addAction(self.action_help)

        self.labelFPS = QLabel("FPS: --")
        self.statusbar.addPermanentWidget(self.labelFPS)
        self.labelInterpreterStatus = QLabel("Interpreter: Offline")
        self.statusbar.addPermanentWidget(self.labelInterpreterStatus)

        self._last_fps_update_time = time.time()
        self.widgetCameraFeed.fps_signal.connect(self._update_fps)

        self.widgetCameraFeed.results_processed.connect(self._handle_frame_results)

        self.widgetControlPanel.inference_toggle_requested.connect(self._toggle_inference)
        self.widgetControlPanel.collection_toggle_requested.connect(self._toggle_data_collection)
        self.widgetControlPanel.status_msg_signal.connect(self.statusbar.showMessage)
        self.widgetControlPanel.model_reload_requested.connect(
            self.widgetPredictions.reload_models
        )

        self.statusbar.showMessage("UI initialized!", 2000)
        print("INFO: UI initialized successfully!")

    def _clear_all(self):
        self.widgetPredictions.clear()
        self.widgetCameraFeed.clear()
        self.widgetControlPanel.clear()
    
    def _toggle_inference(self):
        if not self.mode == AppMode.PREDICTING:
            if self.mode == AppMode.COLLECTING:
                self._toggle_data_collection()

            self._clear_all()
            self.widgetCameraFeed.start_camera()
            self.mode = AppMode.PREDICTING
            self.widgetControlPanel.buttonStartMIRA.setText("Stop M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Online") 
            
        else:
            self.widgetCameraFeed.stop_camera()
            self.widgetPredictions.labelCurrentPrediction.clear()
            self.widgetControlPanel.buttonStartMIRA.setText("Start M.I.R.A.")
            self.labelInterpreterStatus.setText("Interpreter: Offline")
            self.labelFPS.setText("FPS: --")
            self.mode = AppMode.IDLE
    
    def _toggle_data_collection(self):
        if not self.mode == AppMode.COLLECTING:
            if self.mode == AppMode.PREDICTING:
                self._toggle_inference()

            self.widgetPredictions.clear()
            self.widgetCameraFeed.start_camera()
            self.widgetControlPanel.buttonStartTraining.setText("Stop Data Collection")
            self.mode = AppMode.COLLECTING

        else:
            self.widgetCameraFeed.stop_camera()
            self.widgetControlPanel.clear()
            self.widgetControlPanel.buttonStartTraining.setText("Start Data Collection")
            self.labelFPS.setText("FPS: --")
            self.mode = AppMode.IDLE
    
    def _handle_frame_results(self, results):
        if self.mode == AppMode.PREDICTING:
            self.widgetPredictions._predictor._classifier.update(results)
            self.widgetPredictions.predict_and_display(results)
        elif self.mode == AppMode.COLLECTING:
            self.widgetControlPanel.collect_frame(results)                
    
    def _update_fps(self, curr_fps : int):
        curr_time = time.time()
        elapsed_time = curr_time - self._last_fps_update_time

        if elapsed_time >= 1.0:
            self.labelFPS.setText(f"FPS: {curr_fps}")
            self._last_fps_update_time = curr_time