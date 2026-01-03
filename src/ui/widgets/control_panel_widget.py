from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ml.train import Recorder, RecordingType, train_models

from .auto_control_panel_widget import Ui_widgetControlPanel

class ControlPanelWidget(QWidget, Ui_widgetControlPanel):
    inference_toggle_requested = pyqtSignal()
    collection_toggle_requested = pyqtSignal()
    status_msg_signal = pyqtSignal(str, int)
    model_reload_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._recorder = Recorder()

        self.buttonStartMIRA.clicked.connect(self.inference_toggle_requested.emit)
        self.buttonStartTraining.clicked.connect(self.collection_toggle_requested.emit)
        self.comboBoxGestureType.currentIndexChanged.connect(self._pick_recording_type)
        self.buttonSaveRecord.clicked.connect(
            lambda: self._recorder.save_gesture(self.lineEditGestureLabel.text().strip())
        )
        self.buttonRunTraining.clicked.connect(self._run_training)
    
    def clear(self):
        self._recorder.reset()
        self.comboBoxGestureType.setCurrentIndex(0)
        self.lineEditGestureLabel.clear()
    
    def collect_frame(self, results):
        """
        Passes a frame's landmark results to the recorder

        :param results: The processed landmark results from the vision module
        """

        self._recorder.add_frame(results)
    
    def _pick_recording_type(self):
        """
        Picks the recording type based on the current selection in the combo box
        """

        gesture_type = self.comboBoxGestureType.currentText()
        recording_type = None

        if gesture_type == "Static":
            recording_type = RecordingType.STATIC
        elif gesture_type == "Dynamic":
            recording_type = RecordingType.DYNAMIC
        else:
            recording_type = RecordingType.NONE
        
        self._recorder.pick_recording_type(recording_type)
        self.status_msg_signal.emit(f"Recording type set to: {gesture_type}", 2000)
    
    def _run_training(self):
        """
        Triggers the training of the machine learning models and reloads them upon completion
        """

        self.status_msg_signal.emit("Training models...", 5000)
        train_models()
        self.model_reload_requested.emit()
        self.status_msg_signal.emit("Model training completed!", 5000)
