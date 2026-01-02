import time

from PyQt6.QtWidgets import QWidget, QListWidgetItem
from PyQt6.QtCore import Qt

from ml import Predictor

from .auto_predictions_widget import Ui_widgetPredictions

from utils import STATIC_MODEL_PATH

class PredictionsWidget(QWidget, Ui_widgetPredictions):
    _MAX_PREDICTIONS_PER_SECOND = 2
    _MAX_PREDICTIONS_IN_LOG = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._predictor = Predictor(STATIC_MODEL_PATH)

        self._last_prediction_time = 0.0
        self._last_gesture = ""

    def clear(self):
        self.listPredictionLog.clear()
        self.labelCurrentPrediction.setText("-")

        self._last_gesture = ""
        self._last_prediction_time = 0.0

    def predict_and_display(self, results):
        if not results.multi_hand_landmarks:
            self.labelCurrentPrediction.setText("No Hand")
            self._last_gesture = ""
            return

        current_time = time.time()
        if current_time - self._last_prediction_time < 1.0 / self._MAX_PREDICTIONS_PER_SECOND:
            return

        gesture_id = self._predictor.predict(results)
        current_gesture = str(gesture_id)

        self.labelCurrentPrediction.setText(current_gesture)

        if current_gesture != self._last_gesture:
            item = QListWidgetItem(current_gesture)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Insert at the top
            self.listPredictionLog.insertItem(0, item)

            if self.listPredictionLog.count() > self._MAX_PREDICTIONS_IN_LOG:
                self.listPredictionLog.takeItem(self._MAX_PREDICTIONS_IN_LOG)
        
        self._last_gesture = current_gesture
        self._last_prediction_time = current_time
