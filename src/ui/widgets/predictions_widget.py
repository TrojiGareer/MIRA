import time
import traceback

# ADDED: QScrollArea
from PyQt6.QtWidgets import (QWidget, QListWidgetItem, QDialog, QVBoxLayout, 
                             QLabel, QPushButton, QTabWidget, QScrollArea)
from PyQt6.QtCore import Qt

from ml import Predictor
from .auto_predictions_widget import Ui_widgetPredictions
from utils import STATIC_MODEL_PATH, DYNAMIC_MODEL_PATH

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("M.I.R.A. Command Manual")
        self.setFixedSize(400, 320) 

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        self.tab_activation = QWidget()
        self.layout_act = QVBoxLayout()
        lbl_act = QLabel("""
            <h3 style="color:#a05ea0;">System Status</h3>
            <p style="font-size:14px;">👍 <b>Thumbs Up:</b><br>ACTIVATE Mouse Control</p>
            <p style="font-size:14px;">✊ <b>Fist:</b><br>DEACTIVATE Mouse</p>
            <br>
            <p style="color:gray; font-style:italic;">Use these to toggle M.I.R.A. on and off.</p>
        """)
        lbl_act.setWordWrap(True)
        lbl_act.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_act.addWidget(lbl_act)
        self.tab_activation.setLayout(self.layout_act)

        self.tab_mouse = QWidget()
        self.layout_mouse = QVBoxLayout()
        lbl_mouse = QLabel("""
            <h3 style="color:#a05ea0;">Cursor Control</h3>
            <p style="font-size:14px;">☝️ <b>Index Finger:</b><br>Move Cursor</p>
            <p style="font-size:14px;">🤏 <b>Pinch Index + Thumb:</b><br>Left Click / Drag</p>
            <p style="font-size:14px;">🖕 <b>Pinch Middle + Thumb:</b><br>Right Click</p>
        """)
        lbl_mouse.setWordWrap(True)
        lbl_mouse.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_mouse.addWidget(lbl_mouse)
        self.tab_mouse.setLayout(self.layout_mouse)

        self.tab_utils = QWidget()
        self.layout_utils_outer = QVBoxLayout(self.tab_utils)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        self.layout_utils = QVBoxLayout(scroll_content)

        lbl_utils = QLabel("""
            <h3 style="color:#a05ea0;">Windows Shortcuts</h3>
            <p style="font-size:14px;">🤘 <b>Ring Fold (Rock On):</b><br>Open Task View (Win + Tab)</p>
            <p style="font-size:12px; color:gray;">(Keep Index, Middle, Pinky UP. Fold Ring finger)</p>
            
            <hr>
            
            <h3 style="color:#a05ea0;">Scrolling & Audio</h3>
            <p style="font-size:14px;">✌️ <b>Victory Sign:</b> Enable Scroll</p>
            <ul style="font-size:13px;">
                <li>Hand High: Scroll UP</li>
                <li>Hand Low: Scroll DOWN</li>
            </ul>
            <br>
            <p style="font-size:14px;">👐 <b>Two Hands Open:</b> Volume Control</p>
            <ul style="font-size:13px;">
                <li>Move hands apart: Volume UP</li>
                <li>Move hands together: Volume DOWN</li>
            </ul>
        """)
        lbl_utils.setWordWrap(True)
        lbl_utils.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.layout_utils.addWidget(lbl_utils)
        
        scroll.setWidget(scroll_content)
        
        self.layout_utils_outer.addWidget(scroll)

        self.tabs.addTab(self.tab_activation, "Activation")
        self.tabs.addTab(self.tab_mouse, "Mouse")
        self.tabs.addTab(self.tab_utils, "Utils")

        layout.addWidget(self.tabs)

        btn_close = QPushButton("Got it!")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)

class PredictionsWidget(QWidget, Ui_widgetPredictions):
    _MAX_PREDICTIONS_PER_SECOND = 2
    _MAX_PREDICTIONS_IN_LOG = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._predictor = Predictor(STATIC_MODEL_PATH, DYNAMIC_MODEL_PATH)

        self._last_prediction_time = 0.0
        self._last_gesture = ""

    def show_help_dialog(self):
        """Opens the user manual popup. Called by Main Window."""
        dialog = HelpDialog(self)
        dialog.exec()

    def clear(self):
        self.listPredictionLog.clear()
        self.labelCurrentPrediction.setText("-")
        self._last_gesture = ""
        self._last_prediction_time = 0.0
    
    def reload_models(self):
        try:
            self._predictor = Predictor(STATIC_MODEL_PATH, DYNAMIC_MODEL_PATH)
            print("INFO: reloaded models")
        except Exception as e:
            print(f"Error reloading models: {e}")
            traceback.print_exc()

    def predict_and_display(self, results):
        if not results.multi_hand_landmarks:
            self.labelCurrentPrediction.setText("No Hand")
            self._last_gesture = ""
            return

        current_gesture = "noise"
        current_time = time.time()
        if current_time - self._last_prediction_time < 1.0 / self._MAX_PREDICTIONS_PER_SECOND:
            return

        gesture_id = self._predictor.predict(results)
        if current_gesture != gesture_id:
            current_gesture = str(gesture_id)

        self.labelCurrentPrediction.setText(current_gesture)

        if current_gesture != self._last_gesture:
            item = QListWidgetItem(current_gesture)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.listPredictionLog.insertItem(0, item)

            if self.listPredictionLog.count() > self._MAX_PREDICTIONS_IN_LOG:
                self.listPredictionLog.takeItem(self._MAX_PREDICTIONS_IN_LOG)
        
        self._last_gesture = current_gesture
        self._last_prediction_time = current_time