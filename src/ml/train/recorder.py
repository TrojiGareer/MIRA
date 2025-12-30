import csv
import os
from enum import Enum, auto

from preprocess import process_dataset
from utils import (
    DATA_DIR,
    STATIC_GESTURE_TRAINING_DATA_PATH,
    DYNAMIC_GESTURE_TRAINING_DATA_PATH,
)

class RecordingType(Enum):
    """
    Enumeration of supported recording types for hand gesture data
    """
    NONE = auto()
    STATIC = auto()
    STATIC_NOISE = auto()
    DYNAMIC = auto()
    DYNAMIC_NOISE = auto()

class Recorder:
    """
    Helper class for recording and storing hand gesture training sessions
    """

    def __init__(self):
        """
        Ensures the state of the recorder is initialized properly and the training data files exist
        """
        
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Mapping of recording types to their respective filenames
        self.file_map = {
            RecordingType.STATIC: STATIC_GESTURE_TRAINING_DATA_PATH,
            RecordingType.DYNAMIC: DYNAMIC_GESTURE_TRAINING_DATA_PATH,
        }

        # Assert the data type for static type checking
        self.current_working_file : str
        self.current_recording_type : RecordingType

        self._ensure_headers_exist()
    
    def _ensure_headers_exist(self):
        """
        Private helper to initialize CSV files with headers if they do not already exist
        """

        # Header of the static/static noise gestures file
        header_static = ['label'] + [f'left_{i}' for i in range(42)] + [f'right_{i}' for i in range(42)]

        # Header of the dynamic/dynamic noise gestures file
        header_dynamic = ['label']
        for j in range(10):
            header_dynamic += [f'frame_{j}_left_{i}' for i in range(42)] + [f'frame_{j}_right_{i}' for i in range(42)]

        headers = {
            RecordingType.STATIC: header_static,
            RecordingType.DYNAMIC: header_dynamic,
        }
        
        # Create files with headers if they do not exist
        for gesture_type, filepath in self.file_map.items():
            if not os.path.exists(filepath):
                with open(filepath, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers[gesture_type])

    def pick_recording_type(self, recording_type: RecordingType):
        self.current_recording_type = recording_type
        self.current_working_file = self.file_map[recording_type]

        print("INFO: Current recording type: " + str(self.current_recording_type))

    def save_gesture(self, label, results):
        """
        Public method to save a labeled gesture based on the current recording type
        """

        if self.current_recording_type == RecordingType.STATIC or self.current_recording_type == RecordingType.STATIC_NOISE:
            self._save_static_gesture(label, results)
        else:
            print("Warning: Dynamic gesture recording not yet implemented.")

    def _save_static_gesture(self, label, results):
        """
        Private method to process and append a static labeled gesture frame to the currently active CSV file
        
        :param label: The gesture label for this recording
        :param results: MediaPipe hand detection results object
        """
        interpreted_data = process_dataset(results)

        with open(self.current_working_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([label] + interpreted_data)
    
    # # process the 30 images into 10 and store them
    # def add_video_data(self):
    #     # make sure lag doesnt impact things
    #     if len(self.video_frames_raw) < 30:
    #         print(f"Error: Buffer underflow. Got {len(self.video_frames_raw)}/30 frames.")
    #         self.video_frames_raw = []
    #         self.session_recording_count = 0
    #         return
        
    #     final_video_data = []
    #     for i in range(0, 30, 3):
    #         final_video_data.extend(self.video_frames_raw[i])

    #     with open(self.filepath, mode='a', newline='') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([self.current_gesture_label] + final_video_data)
            
    #     self.video_frames_raw = []
    #     self.session_recording_count = 0

    # def add_frame_to_current_video(self, results):
    #     processed_raw_frame = process_dataset(results)
    #     self.video_frames_raw.append(processed_raw_frame)

    def reset(self):
        self.current_working_file = ""
        self.current_recording_type = RecordingType.NONE
