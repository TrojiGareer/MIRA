import pickle
import numpy as np
from preprocess.landmark_extractor import process_dataset

class Interpreter:
    def __init__(self, model_path='model.p'):
        self.model = None
        self.labels_dict = {}
        self.load_model(model_path)
    
    def load_model(self, path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
        except FileNotFoundError:
            self.model = None

    def predict(self, results):
        if self.model is None or results is None:
            return "error"

        processed_data = process_dataset(results)
        data_array = np.array([processed_data])
        prediction = self.model.predict(data_array)[0]
        return prediction