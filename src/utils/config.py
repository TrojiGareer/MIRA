import os

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(UTILS_DIR)

UI_DIR = os.path.join(SRC_DIR, "ui")
UI_FILE_PATH = os.path.join(UI_DIR, "main_window.ui")

ML_DIR = os.path.join(SRC_DIR, "ml")
STATIC_MODEL_PATH = os.path.join(ML_DIR, "static_model.p")

TRAIN_DIR = os.path.join(ML_DIR, "train")
DATA_DIR = os.path.join(TRAIN_DIR, "data")
STATIC_GESTURE_TRAINING_DATA_PATH = os.path.join(DATA_DIR, "static_gestures_training_data.csv")
DYNAMIC_GESTURE_TRAINING_DATA_PATH = os.path.join(DATA_DIR, "dynamic_gestures_training_data.csv")