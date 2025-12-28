import math

class Classifier:
    # calculates a score that allows it to decide whether or not a movement is noise or a gesture
    def __init__(self):
        self.score = 0
        self.past_half_second_frames = []

    # steady hand and moving fingers is usually just sign transition
    def finger_movement(self, landmarks):
        return
    
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

    # a hand that bolts through the screen is likely being moved outside of it, not a sign
    def translation_speed(self, landmarks):
        return

    # gestures are usually perfect lines, curves or circles
    def trajectory(self, landmarks):
        return

    # a hand holding a sign is usually pretty stable, jitters might indicate a data extraction error
    def stability(self, landmarks):
        return

    # update function
    def update(self):
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


    