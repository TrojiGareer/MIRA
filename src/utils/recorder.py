import csv
import os
from preprocess.landmark_extractor import process_landmarks

class Recorder:
    # initialize the object and the file if it doesnt exist

    def __init__(self, filepath='hand_data.csv'):
        self.current_gesture = None
        self.filepath = filepath
        
        # create the file if it doesnt exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as f:
                writer = csv.writer(f)
                # header: label, coord_0, coord_1 ... coord_41
                header = ['label'] + [f'coord_{i}' for i in range(42)]
                writer.writerow(header)

    # add a row in the csv table

    def add_record(self, label, raw_landmarks):
        interpreted_data = process_landmarks(raw_landmarks)

        with open(self.filepath, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([label] + interpreted_data)

