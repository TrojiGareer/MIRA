import math
import numpy as np
from .executor import Executor

class CommandMapper:
    def __init__(self):
        self.executor = Executor()
        
        self.is_active = False  
        self.is_pinching_left = False
        self.is_pinching_right = False
        self.last_volume_dist = None
        
        self.activation_counter = 0
        self.deactivation_counter = 0
        self.STATE_CHANGE_FRAMES = 10 

        self.CLICK_THRESHOLD = 0.05
        self.FREEZE_THRESHOLD = 0.10 
        self.FRAME_MARGIN = 0.2 

    def process_results(self, results):
        if not results.multi_hand_landmarks:
            return

        hand_landmarks_list = results.multi_hand_landmarks
        first_hand = hand_landmarks_list[0]

        self._handle_state_switching(first_hand)

        if not self.is_active:
            return

        if len(hand_landmarks_list) == 2:
            self._handle_volume_control(hand_landmarks_list[0], hand_landmarks_list[1])
            return 

        self._handle_mouse_and_scroll(first_hand)

    def _is_finger_curled(self, landmarks, tip_idx, pip_idx):
        wrist = landmarks.landmark[0]
        tip = landmarks.landmark[tip_idx]
        pip = landmarks.landmark[pip_idx]

        dist_tip_wrist = self._calculate_distance(tip, wrist)
        dist_pip_wrist = self._calculate_distance(pip, wrist)

        return dist_tip_wrist < dist_pip_wrist

    def _handle_state_switching(self, landmarks):
        thumb_tip = landmarks.landmark[4]
        index_mcp = landmarks.landmark[5] 
        wrist = landmarks.landmark[0]

        index_curled = self._is_finger_curled(landmarks, 8, 6)
        middle_curled = self._is_finger_curled(landmarks, 12, 10)
        ring_curled = self._is_finger_curled(landmarks, 16, 14)
        pinky_curled = self._is_finger_curled(landmarks, 20, 18)

        fingers_folded = middle_curled and ring_curled and pinky_curled and index_curled
        thumb_is_high = thumb_tip.y < (index_mcp.y - 0.02)
        
        if fingers_folded:
            if thumb_is_high:
                self.activation_counter += 1
                self.deactivation_counter = 0 
                if self.activation_counter > self.STATE_CHANGE_FRAMES:
                    if not self.is_active:
                        self.is_active = True
                        print(">>> MODE SWITCHED: ACTIVE (Mouse On) <<<")
                    self.activation_counter = 0 
            else:
                self.deactivation_counter += 1
                self.activation_counter = 0
                if self.deactivation_counter > self.STATE_CHANGE_FRAMES:
                    if self.is_active:
                        self.is_active = False
                        print(">>> MODE SWITCHED: SLEEP (Mouse Off) <<<")
                    self.deactivation_counter = 0
        else:
            if self.activation_counter > 0:
                 self.activation_counter -= 1
            self.deactivation_counter = 0

    def _handle_mouse_and_scroll(self, landmarks):
        thumb = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]  
        index_mcp = landmarks.landmark[5]  
        middle = landmarks.landmark[12]
        
        index_curled = self._is_finger_curled(landmarks, 8, 6)
        middle_curled = self._is_finger_curled(landmarks, 12, 10)
        ring_curled = self._is_finger_curled(landmarks, 16, 14)
        pinky_curled = self._is_finger_curled(landmarks, 20, 18)

        is_ring_fold = (not index_curled) and (not middle_curled) and ring_curled and (not pinky_curled)

        if is_ring_fold:
            if self.activation_counter == 0:
                self.executor.switch_window()
                print("Keyboard: Win + Tab")
                self.activation_counter = 30
            return

        is_victory_sign = (not index_curled) and (not middle_curled) and ring_curled and pinky_curled

        if is_victory_sign:
            hand_y = landmarks.landmark[9].y 
            if hand_y < 0.4:
                self.executor.scroll(1) 
            elif hand_y > 0.6:
                self.executor.scroll(-1) 
            return 

        dist_left = self._calculate_distance(index_tip, thumb)
        should_move = (dist_left > self.FREEZE_THRESHOLD) or self.is_pinching_left

        if should_move:
            raw_x = index_mcp.x
            raw_y = index_mcp.y
            x_mapped = np.interp(raw_x, [self.FRAME_MARGIN, 1.0 - self.FRAME_MARGIN], [0, 1])
            y_mapped = np.interp(raw_y, [self.FRAME_MARGIN, 1.0 - self.FRAME_MARGIN], [0, 1])
            self.executor.move_mouse(1.0 - x_mapped, y_mapped)

        if dist_left < self.CLICK_THRESHOLD:
            if not self.is_pinching_left:
                self.is_pinching_left = True
                self.executor.start_drag()
        else:
            if self.is_pinching_left:
                self.is_pinching_left = False
                self.executor.stop_drag()

        dist_right = self._calculate_distance(middle, thumb)
        if dist_right < self.CLICK_THRESHOLD:
            if not self.is_pinching_right:
                self.is_pinching_right = True
                self.executor.right_click()
        else:
            self.is_pinching_right = False

    def _handle_volume_control(self, hand1, hand2):
        idx1 = hand1.landmark[8]
        idx2 = hand2.landmark[8]
        current_dist = self._calculate_distance(idx1, idx2)

        if self.last_volume_dist is None:
            self.last_volume_dist = current_dist
            return

        delta = current_dist - self.last_volume_dist
        if delta > 0.02:
            self.executor.change_volume("up")
            self.last_volume_dist = current_dist
        elif delta < -0.02:
            self.executor.change_volume("down")
            self.last_volume_dist = current_dist

    def _calculate_distance(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)