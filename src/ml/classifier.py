import math
from enum import Enum, auto

class Gesture(Enum):
    NONE = auto()
    NOISE = auto()
    STATIC = auto()
    DYNAMIC = auto()

class Classifier:
    # calculates a score that allows it to decide whether or not a movement is noise or a gesture
    def __init__(self):
        self.score = 0
        self.past_20_frames = []
        self.past_frame_count = 0
        self.last_classification = 0
        self.crt_gesture = Gesture.NONE

    # called every frame, gathers the past 20 frames at all times
    def update(self, results):
        self.past_20_frames.append(results)
        self.past_frame_count += 1

        if self.past_frame_count > 20:
            self.past_20_frames.pop(0)

    def calculate_movement_type(self):
        if len(self.past_20_frames) < 20:
            return "noise"
        
        last_frame = self.past_20_frames[19]
        if not last_frame.multi_hand_landmarks:
            return "noise"
        last_frame = last_frame.multi_hand_landmarks[0]
        hand_scale = math.sqrt((last_frame.landmark[9].x - last_frame.landmark[0].x)**2 + (last_frame.landmark[9].y - last_frame.landmark[0].y)**2)

        if hand_scale < 0.01:
            return "noise"

        # for wrist
        hand_translation = (self.translation(0) / 2 + self.translation(9) / 2) / hand_scale
        finger_wiggle =  self.finger_movement()
        
        if hand_translation > 0.9:
            self.crt_gesture = Gesture.DYNAMIC
            return "dynamic"
        else:
            if finger_wiggle > 0.0008:
                self.crt_gesture = Gesture.NOISE
                return "noise"
            else:
                self.crt_gesture = Gesture.STATIC
                return "static"


    # steady hand and moving fingers is usually just sign transition
    def finger_movement(self):
        if len(self.past_20_frames) < 20: 
            return 0.0

        distances = []

        for res in self.past_20_frames:
            if not res.multi_hand_landmarks: 
                continue
            
            lm = res.multi_hand_landmarks[0].landmark
            frame_distances = []
            dist_index = math.sqrt((lm[8].x - lm[0].x)**2 + (lm[8].y - lm[0].y)**2)
            frame_distances.append(dist_index)

            dist_middle = math.sqrt((lm[12].x - lm[0].x)**2 + (lm[12].y - lm[0].y)**2)
            frame_distances.append(dist_middle)

            dist_ring = math.sqrt((lm[16].x - lm[0].x)**2 + (lm[16].y - lm[0].y)**2)
            frame_distances.append(dist_ring)

            dist_pinky = math.sqrt((lm[20].x - lm[0].x)**2 + (lm[20].y - lm[0].y)**2)
            frame_distances.append(dist_pinky)

            distances.append(frame_distances)

        if not distances: 
            return 0.0

        # average distances each finger moved
        avg_dist = []
        for i in range(4):
            avg_dist.append(sum(row[i] for row in distances) / len(distances))

        total_wiggle_score = 0

        for row in distances:
            for i in range(len(row)):
                deviation = row[i] - avg_dist[i]
                total_wiggle_score += (deviation ** 2)


        final_score = total_wiggle_score / len(distances)

        return final_score
    
    # a relaxed hand has a specific shape, that can be calculated
    def relaxation_factor(self, results):
        # for now just for one hand
        fingers = self.get_finger_joints(results)
        tense_fingers = 0
        for finger in fingers:
            angle = self.finger_relaxation(finger)
            if (angle > 80) or (angle < 20):
                tense_fingers += 1

        # 0 for relaxed, 1 for sign
        if tense_fingers >= 3:
            return 1
        else:
            return 0

    def decide_relaxation(self, results):
        index = 0
        self.past_half_second_frames.append(results)
        for frame in self.past_half_second_frames:
            index += self.relaxation_factor(frame)
        if (len(self.past_half_second_frames) / 2 < index):
            # majority voted for
            return "sign"
        else:
            return "relaxed"


    # a human bias to center their hand on the screen when performing relevant actions
    def center_bias(self, landmarks):
        return

    # dynamic movement will most likely involve the translation of the hand on screen
    # static movement or signs is usually just moving of the fingers
    def translation(self, point):
        total_distance = 0
        for i in range(19):
            curr_res = self.past_20_frames[i]
            next_res = self.past_20_frames[i+1]

            # if for a frame the camera tweaked
            if not (curr_res.multi_hand_landmarks and next_res.multi_hand_landmarks):
                continue
            
            curr = curr_res.multi_hand_landmarks[0].landmark[point]
            flwing = next_res.multi_hand_landmarks[0].landmark[point]

            # distance the wrist moved the past 2 frames
            step_dist = math.sqrt((flwing.x - curr.x)**2 + (flwing.y - curr.y)**2)
            
            total_distance += step_dist
        return total_distance

    # gestures are usually perfect lines, curves or circles
    def trajectory(self, landmarks):
        return

    # a hand holding a sign is usually pretty stable, jitters might indicate a data extraction error
    def stability(self, landmarks):
        return

    # determine if a specific finger is relaxed or not
    # assumes an array of 8 coordinates of knuckle, mid joint, final joint and tip of a finger
    def finger_relaxation(self, finger_data):
        # analyze them 3 at a time, first knuckle, mid, final joint
        a = finger_data[2] - finger_data[0]
        b = finger_data[3] - finger_data[1]
        first = (a, b)
        first_len = math.sqrt(first[0] * first[0] + first[1] * first[1])

        a = finger_data[4] - finger_data[2]
        b = finger_data[5] - finger_data[3]
        second = (a, b)
        second_len = math.sqrt(second[0] * second[0] + second[1] * second[1])

        if first_len == 0 or second_len == 0:
            return 0

        cos = ((first[0] * second[0]) + (first[1] * second[1])) / (first_len * second_len)
        cos = max(-1.0, min(1.0, cos))

        angle_rad = math.acos(cos)
        return math.degrees(angle_rad)

    def get_finger_joints(self, results):
        if not results.multi_hand_landmarks:
            return []

        hand_landmarks = results.multi_hand_landmarks[0].landmark
        fingers = []

        for i in range(1, 21, 4):
            crt_finger = []
            
            for j in range(i, i + 4):
                crt_finger.append(hand_landmarks[j].x)
                crt_finger.append(hand_landmarks[j].y)
            
            fingers.append(crt_finger)
        return fingers
