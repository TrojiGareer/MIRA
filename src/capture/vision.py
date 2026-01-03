import cv2
import numpy as np
import mediapipe as mp

class Vision:
    """
    Preprocessing bridge between mediapipe hands and the live camera feed.
    Puts the hands onto the feed
    """

    def __init__(self):
        self.mp_hands = mp.solutions.hands # type: ignore (runtime only)
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_draw = mp.solutions.drawing_utils # type: ignore (runtime only)
        self.mp_styles = mp.solutions.drawing_styles # type: ignore (runtime only)
        
    def process_frame(self, frame:np.ndarray):
        """
        Puts the mediapipe hands vertices and skeleton on top of the recorded frame and flips the image
        for better UX

        :param self: the instance of the Vision class
        :param frame: the frame to process, in openCV format (bgr)

        :return frame: the processed frame with hands drawn on it, mirrored (bgr)
        :return results: mediapipe results object from a frame
        """

        # bgr->rgb for mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            self.draw_landmarks(frame, results)

        # mirror the image
        frame = cv2.flip(frame, 1)
        return frame, results

    def draw_landmarks(self, frame, results):
        """
        Draws the hands onto a frame

        :param self: the instance of the Vision class
        :param frame: the frame to draw on, in openCV format (bgr)
        :param results: mediapipe results object from a frame
        """

        for landmarks in results.multi_hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_styles.get_default_hand_landmarks_style(),
                self.mp_styles.get_default_hand_connections_style()
            )
