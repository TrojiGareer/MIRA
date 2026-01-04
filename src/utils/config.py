import os

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(UTILS_DIR)

UI_DIR = os.path.join(SRC_DIR, "ui")
STYLESHEET_PATH = os.path.join(UI_DIR, "style.qss")
WIDGETS_DIR = os.path.join(UI_DIR, "widgets")

ML_DIR = os.path.join(SRC_DIR, "ml")
STATIC_MODEL_PATH = os.path.join(ML_DIR, "static_model.p")
DYNAMIC_MODEL_PATH = os.path.join(ML_DIR, "dynamic_model.p")

TRAIN_DIR = os.path.join(ML_DIR, "train")
DATA_DIR = os.path.join(TRAIN_DIR, "data")
STATIC_GESTURE_TRAINING_DATA_PATH = os.path.join(DATA_DIR, "static_gestures_training_data.csv")
DYNAMIC_GESTURE_TRAINING_DATA_PATH = os.path.join(DATA_DIR, "dynamic_gestures_training_data.csv")