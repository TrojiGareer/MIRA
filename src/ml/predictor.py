import pickle
import numpy as np
import os

from preprocess import process_dataset
from ml.classifier import Classifier, Gesture

class Predictor:
    def __init__(self, static_model_path : str, dynamic_model_path : str):
        self.static_model = self.load_model(static_model_path)
        self.dynamic_model = self.load_model(dynamic_model_path)
        self._classifier = Classifier()

    def load_model(self, path):
        if not os.path.exists(path):
            print(f"ERROR: Model file at {path} doesn't exist.")
            return None

        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, dict) and 'model' in data:
                    print(f"INFO: Loaded dictionary model from {path}")
                    return data['model']
                else:
                    print(f"INFO: Loaded raw model object from {path}")
                    return data
        except Exception as e:
            print(f"ERROR: Failed to load {path}: {e}")
            return None

    def predict(self, results):
        if self.static_model is None or self.dynamic_model is None:
            return "model not loaded or invalid results"
        
        self._classifier.calculate_movement_type()

        if self._classifier.crt_gesture == Gesture.STATIC:
            processed_data = process_dataset(self._classifier.past_30_frames[29])
            data_array = np.array([processed_data])
            prediction = self.static_model.predict(data_array)[0]
            return prediction
        elif self._classifier.crt_gesture == Gesture.DYNAMIC:
            dynamic_row = []
            
            for frame in self._classifier.past_30_frames:
                features = process_dataset(frame) 
                dynamic_row.extend(features)
            
            prediction = self.dynamic_model.predict(np.array([dynamic_row]))[0]
            return prediction
        else:
            return self._classifier.calculate_movement_type()
