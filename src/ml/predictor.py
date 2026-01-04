import pickle
import numpy as np

from preprocess import process_dataset
from ml.classifier import Classifier, Gesture

class Predictor:
    def __init__(self, model_path : str):
        self.load_model(model_path)
        self._classifier = Classifier()

    def load_model(self, path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
        except FileNotFoundError:
            print(f"model file at {path} doesnt exist")
            self.model = None

    def predict(self):
        if self.model is None:
            return "model not loaded or invalid results"
        
        self._classifier.calculate_movement_type()

        if self._classifier.crt_gesture == Gesture.STATIC:
            processed_data = process_dataset(self._classifier.past_20_frames[19])
            data_array = np.array([processed_data])
            prediction = self.model.predict(data_array)[0]
            return prediction
        else:
            return self._classifier.calculate_movement_type()
