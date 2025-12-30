import pickle
import numpy as np

from preprocess import process_dataset

class Predictor:
    """
    A wrapper class for using a chosen trained model to predict hand gestures
    """

    def __init__(self, model_path : str):
        self.load_model(model_path)

    def load_model(self, path):
        """
        Loads a trained model from the given path
        
        :param path: Path to the trained model file
        """

        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
        except FileNotFoundError:
            print(f"ERROR: Model file at {path} not found! Make sure to train a model first.")
            self.model = None

    def predict(self, results):
        """
        Makes a prediction based on the given MediaPipe results using the loaded model
        
        :param results: MediaPipe hand detection results object
        :return: Predicted gesture label (string)
        """

        if self.model is None or results is None:
            return "Model not loaded or invalid results"

        processed_data = process_dataset(results)
        data_array = np.array([processed_data])
        # It is assumed that the model has a predict() method
        prediction = self.model.predict(data_array)[0]
        return prediction
