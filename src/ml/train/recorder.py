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
    DYNAMIC = auto()

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
            RecordingType.NONE: "",
            RecordingType.STATIC: STATIC_GESTURE_TRAINING_DATA_PATH,
            RecordingType.DYNAMIC: DYNAMIC_GESTURE_TRAINING_DATA_PATH,
        }

        # Assert the data type for static type checking
        self.current_working_file : str

        self.current_recording_type = RecordingType.NONE
        self._buffer = []

        # added a recording buffer, for storing different types of input
        self._video_buffer = []
        self._video_frame_count = 0
        self._recording_active = False
        self._pending_label = ""

        self._ensure_headers_exist()
    
    def reset(self):
        self.current_working_file = ""
        self.current_recording_type = RecordingType.NONE
        self._buffer = []
        self._video_buffer = []
        self._video_frame_count = 0
    
    def _ensure_headers_exist(self):
        """
        Private helper to initialize CSV files with headers if they do not already exist
        """

        # Header of the static/static noise gestures file
        header_static = ['label'] + [f'left_{i}' for i in range(42)] + [f'right_{i}' for i in range(42)]

        # Header of the dynamic/dynamic noise gestures file
        header_dynamic = ['label']
        for j in range(30):
            header_dynamic += [f'frame_{j}_left_{i}' for i in range(42)] + [f'frame_{j}_right_{i}' for i in range(42)]

        headers = {
            RecordingType.STATIC: header_static,
            RecordingType.DYNAMIC: header_dynamic,
        }
        
        # Create files with headers if they do not exist
        for gesture_type, filepath in self.file_map.items():
            if not os.path.exists(filepath) and gesture_type != RecordingType.NONE:
                with open(filepath, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers[gesture_type])

    def pick_recording_type(self, recording_type: RecordingType):
        self.reset()
        self.current_recording_type = recording_type
        self.current_working_file = self.file_map[recording_type]

        print("INFO: Current recording type: " + str(self.current_recording_type))
    
    # this happens every frame
    def add_frame(self, results):
        """
        Adds a frame's landmark results to the recording buffer

        :param results: The processed landmark results from the vision module
        """

        if self.current_recording_type == RecordingType.STATIC:
            self._buffer = [results]
            
        elif self.current_recording_type == RecordingType.DYNAMIC:
            if self._recording_active:
                crt_frames = process_dataset(results)
                self._video_buffer.append(crt_frames)
                self._video_frame_count += 1
                print(f"Recorded {self._video_frame_count} / 30 frames")
                
                if len(self._video_buffer) >= 30:
                    self._save_dynamic_gesture(self._pending_label)
                    self._recording_active = False
                    self._video_buffer = []
                    self._video_frame_count = 0
                    print(f"INFO: FINISHED recording sequence.")
        else:
            print("ERROR: No recording type selected. Cannot add frame.")

    # this happens when user hits "record"
    def save_gesture(self, label):
        """
        Public method to save a labeled gesture based on the current recording type
        """

        if self.current_recording_type == RecordingType.STATIC:
            if not self._buffer: return
            self._save_static_gesture(label, self._buffer[0])
            
        elif self.current_recording_type == RecordingType.DYNAMIC:
            self._video_buffer = []
            self._pending_label = label
            self._recording_active = True
            print(f"INFO: STARTED recording sequence for '{label}'...")
        else:
            print("ERROR: No recording type selected. Cannot save gesture.")

    def _save_static_gesture(self, label, results):
        """
        Private method to process and append a static labeled gesture frame to the currently active CSV file
        
        :param label: The gesture label for this recording
        :param results: MediaPipe hand detection results object
        """
        interpreted_data = process_dataset(results)

        with open(self.current_working_file, mode='a', newline='') as f:
            if (f.tell() == 0):
                print(f"Error: File {self.current_working_file} is empty. Cannot write data without headers.")
                return
            writer = csv.writer(f)
            writer.writerow([label] + interpreted_data)

    def _save_dynamic_gesture(self, label):
        with open(self.current_working_file, mode='a', newline='') as f:
            if (f.tell() == 0):
                print(f"Error: File {self.current_working_file} is empty. Cannot write data without headers.")
                return
            flat_video_data = [coordinate for frame in self._video_buffer for coordinate in frame]
            writer = csv.writer(f)
            writer.writerow([label] + flat_video_data)
        return
