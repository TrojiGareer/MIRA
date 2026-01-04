import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils import (
    STATIC_GESTURE_TRAINING_DATA_PATH,
    DYNAMIC_GESTURE_TRAINING_DATA_PATH,
    STATIC_MODEL_PATH,
    DYNAMIC_MODEL_PATH,
)

def _train_model(path, data_path):
    """
    Trains a Random Forest Classifier on the static hand gesture dataset and saves the trained model
    """

    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: {data_path} not found! Go collect some data first.")
        return

    if data.empty:
        print(f"Error: {data_path} is empty! Go collect some data first.")
        return

    model_type = ""
    if path == STATIC_MODEL_PATH:
        model_type = "static"
    else:
        model_type = "dynamic"

    # x is a matrix of data, y is a vector of labels
    X = data.drop('label', axis=1)
    y = data['label']

    # Split the training data into the one fed to the model and the one testing it
    # 80% training, 20% accuracy testing
    X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.2, shuffle=True, stratify=y)

    model = RandomForestClassifier()
    # The actual training
    model.fit(X_train, y_train)

    # Evaluate the accuracy
    y_predict = model.predict(X_test)
    score = accuracy_score(y_test, y_predict)
    print(f"{model_type} model accuracy: {score * 100:.2f}% ({score})")

    # Save the trained model
    with open(path, 'wb') as f:
        pickle.dump({'model' : model}, f)

def train_models():
    """
    Trains the static and dynamic hand gesture models with a given dataset and saves the trained models
    """

    print("====== Starting models training ======")
    _train_model(STATIC_MODEL_PATH, STATIC_GESTURE_TRAINING_DATA_PATH)
    _train_model(DYNAMIC_MODEL_PATH, DYNAMIC_GESTURE_TRAINING_DATA_PATH)
    print("====== Models training completed ======")

if __name__ == "__main__":
    train_models()