from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ml.train import Recorder

from .auto_control_panel_widget import Ui_widgetControlPanel

class ControlPanelWidget(QWidget, Ui_widgetControlPanel):
    inference_toggle_requested = pyqtSignal()
    collection_toggle_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._recorder = Recorder()

        self.buttonStartMIRA.clicked.connect(self.inference_toggle_requested.emit)
        self.buttonStartTraining.clicked.connect(self.collection_toggle_requested.emit)
    
    def clear(self):
        self._recorder.reset()
        self.comboBoxGestureType.setCurrentIndex(0)
        self.lineEditGestureLabel.clear()
    
    def handle_frame_results(self, results):
        """
        Handles the frame results during data collection mode by passing them to the recorder.

        :param results: The processed results from the camera feed
        """

        gesture_label = self.lineEditGestureLabel.text().strip()
