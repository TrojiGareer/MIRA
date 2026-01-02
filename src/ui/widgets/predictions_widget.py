from PyQt6.QtWidgets import QWidget
from .auto_predictions_widget import Ui_widgetPredictions

class PredictionsWidget(QWidget, Ui_widgetPredictions):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
