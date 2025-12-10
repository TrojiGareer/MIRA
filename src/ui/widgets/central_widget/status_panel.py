from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class StatusPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Gesture Prediction Display
        self.lbl_gesture_header = QLabel("Predicted Gesture")
        self.lbl_predicted_gesture = QLabel("OPEN HAND (IDLE)")
        self.lbl_confidence = QLabel("Confidence: 0%")

        # Action Log
        self.lbl_last_action_title = QLabel("Action Log:")
        self.lbl_last_action = QLabel("Last Action: None")

        # Control Buttons
        self.btn_toggle_inference = QPushButton("Start M.I.R.A.")
        self.btn_data_collection = QPushButton("Start Data Recording")
        self.btn_train_model = QPushButton("Open Training Pipeline")
        
        # Layout the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(self.lbl_gesture_header, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_predicted_gesture, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_confidence, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        
        layout.addWidget(self.lbl_last_action_title)
        layout.addWidget(self.lbl_last_action)
        layout.addSpacing(30)
        
        layout.addWidget(self.btn_toggle_inference)
        layout.addWidget(self.btn_data_collection)
        layout.addWidget(self.btn_train_model)
        
        # layout.addStretch(1) # Pushes controls to the top
