import csv
import os
from preprocess import process_dataset

class Recorder:
    # initialize the object and the file if it doesnt exist

    def __init__(self, filepath_static='static_hand_data.csv', filepath_video='video_hand_data.csv', filepath_noise='noise_hand_data.csv'):
        # the label typed in by the user
        self.current_gesture = ""
        # stage of recording - false for label phase, true for the frames recording part
        self.is_stage_2_recording = False
        # amount of 30-frame inputs gathered in the current recording
        self.session_recording_count = 0
        # amount of recordings gathered since start
        self.recordings = 0
        # hand descriptor (left, right, both_hands)
        self.hand_descriptor = None
        # the raw unprocessed results of a single frame
        self.current_results = None
        # the raw unprocessed 30 frames in a second 
        self.video_frames_raw = []
        self.is_recording = False

        # files for storing data by type and scope
        self.filepath_static = filepath_static
        self.filepath_video = filepath_video
        self.filepath_noise = filepath_noise
        self.filepath = None
        self.scope = "unknown"
        
        # create the files if they dont exist
        if not os.path.exists(self.filepath_static):
            with open(self.filepath_static, mode='w', newline='') as f:
                writer = csv.writer(f)
                header = ['label'] + [f'left_{i}' for i in range(42)] + [f'right_{i}' for i in range(42)]
                writer.writerow(header)

        if not os.path.exists(self.filepath_video):
            with open(self.filepath_video, mode='w', newline='') as f:
                writer = csv.writer(f)
                header = ['label']
                for j in range(10):
                    header += [f'frame_{j}_left_{i}' for i in range(42)] + [f'frame_{j}_right_{i}' for i in range(42)]
                writer.writerow(header)

        if not os.path.exists(self.filepath_noise):
            with open(self.filepath_noise, mode='w', newline='') as f:
                writer = csv.writer(f)
                header = ['label']
                for j in range(10):
                    header += [f'frame_{j}_left_{i}' for i in range(42)] + [f'frame_{j}_right_{i}' for i in range(42)]
                writer.writerow(header)

    # add a row in the csv table
    def add_record(self, label, results):
        interpreted_data = process_dataset(results)

        with open(self.filepath, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([label] + interpreted_data)
    
    # process the 30 images into 10 and store them
    def add_video_data(self):
        # make sure lag doesnt impact things
        if len(self.video_frames_raw) < 30:
            print(f"Error: Buffer underflow. Got {len(self.video_frames_raw)}/30 frames.")
            self.video_frames_raw = []
            self.session_recording_count = 0
            return
        
        final_video_data = []
        for i in range(0, 30, 3):
            final_video_data.extend(self.video_frames_raw[i])

        with open(self.filepath, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.current_gesture] + final_video_data)
            
        self.video_frames_raw = []
        self.session_recording_count = 0

    def add_frame_to_current_video(self, results):
        processed_raw_frame = process_dataset(results)
        self.video_frames_raw.append(processed_raw_frame)

    def pick_data_file(self):
        if self.scope == "static":
            self.filepath = self.filepath_static
        elif self.scope == "video":
            self.filepath = self.filepath_video
        else:
            self.filepath = self.filepath_noise
        print("recording scope defined as:" + self.scope)

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

    def reset(self):
        self.current_gesture = ""
        # stage of recording - false for label phase, true for the frames recording part
        self.is_stage_2_recording = False
        # amount of 30-frame inputs gathered in the current session
        self.session_recording_count = 0
        # hand descriptor (left, right, both_hands)
        self.hand_descriptor = None
        # the raw unprocessed results of a single frame
        self.current_results = None
        # the raw unprocessed 30 frames in a second 
        self.video_frames_raw = []

        self.filepath = None
        self.scope = "unknown"

