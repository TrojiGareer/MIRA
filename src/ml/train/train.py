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
)

def _train_static_model():
    """
    Trains a Random Forest Classifier on the static hand gesture dataset and saves the trained model
    """

    try:
        data = pd.read_csv(STATIC_GESTURE_TRAINING_DATA_PATH)
    except FileNotFoundError:
        print(f"Error: {STATIC_GESTURE_TRAINING_DATA_PATH} not found! Go collect some data first.")
        return

    if data.empty:
        print(f"Error: {STATIC_GESTURE_TRAINING_DATA_PATH} is empty! Go collect some data first.")
        return

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
    print(f"Static model accuracy: {score * 100:.2f}% ({score})")

    # Save the trained model
    with open(STATIC_MODEL_PATH, 'wb') as f:
        pickle.dump({'model': model}, f)

def train_models():
    """
    Trains the static and dynamic hand gesture models with a given dataset and saves the trained models
    """

    print("====== Starting model training ======")

    print("Training static hand gesture model...")
    _train_static_model()
    print("Static hand gesture model trained and saved.")

    # Future implementation for dynamic model training can be added here
    print("Dynamic hand gesture model training not yet implemented.")

    print("====== Model training completed ======")

if __name__ == "__main__":
    train_models()