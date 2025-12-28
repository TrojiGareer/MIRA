import csv
import os
from preprocess.landmark_extractor import process_dataset

class Recorder:
    # initialize the object and the file if it doesnt exist

    def __init__(self, filepath='hand_data.csv'):
        # the label typed in by the user
        self.current_gesture = ""
        # the buffer for storing the frames
        self.current_raw_landmarks = None
        # stage of recording - false for label phase, true for the frames recording part
        self.is_stage_2_recording = False
        # amount of 30-frame inputs gathered in the current session
        self.session_recording_count = 0
        # hand descriptor (left, right, both_hands)
        self.hand_descriptor = None
        self.current_results = None

        self.filepath = filepath
        
        # create the file if it doesnt exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as f:
                writer = csv.writer(f)
                # header: label, coord_0, coord_1 ... coord_84
                header = ['label'] + [f'left_{i}' for i in range(42)] + [f'right_{i}' for i in range(42)]
                writer.writerow(header)

    # add a row in the csv table
    def add_record(self, label, results):
        interpreted_data = process_dataset(results)

        with open(self.filepath, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([label] + interpreted_data)

    # this is just for debugging
    def hand_recognition(self, results):
        # if there is one hand
        if results.multi_hand_landmarks:
            hands = len(results.multi_hand_landmarks)
            if hands == 2:
                self.hand_descriptor = "both_hands"
            else:
                if results.multi_handedness[0].classification[0].label == "Right":
                    self.hand_descriptor = "left"
                else:
                    self.hand_descriptor = "right"
            return self.hand_descriptor

