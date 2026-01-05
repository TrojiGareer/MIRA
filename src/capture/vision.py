import mediapipe as mp
import numpy as np
import cv2
from PyQt6.QtGui import QImage, QPixmap

# object responsible for everything image-related
class Vision:
    def __init__(self):
        # initialize mediapipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        
    # function called every frame to create the ui return image and the mediapipe results
    def process_frame(self, frame:np.ndarray):
        # bgr->rgb for mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            self.draw_landmarks(frame, results)

        # mirror the image
        frame = cv2.flip(frame, 1)
        return frame, results

    # genuinley just draws the landmarks on the frame it gets called to
    def draw_landmarks(self, frame, results):
        for landmarks in results.multi_hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_styles.get_default_hand_landmarks_style(),
                self.mp_styles.get_default_hand_connections_style()
            )

    # translator so that it can actually be in the ui
    def convert_cv_to_pixmap(self, frame: np.ndarray, width: int, height: int) -> QPixmap:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        return QPixmap.fromImage(q_img)

