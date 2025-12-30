import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
try:
    data = pd.read_csv('../hand_data.csv')
except FileNotFoundError:
    print("Error: hand_data.csv not found! Go collect some data first.")
    exit()

if data.empty:
    print("Error: hand_data.csv is empty! Go collect some data first.")
    exit()

# x is all the data, y is just the label
X = data.drop('label', axis=1)
y = data['label']

# 80% training, 20% accuracy testing
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, stratify=y)

# random forest classifier just for testing for now
model = RandomForestClassifier()
model.fit(x_train, y_train)

# evaluate the accuracy
y_predict = model.predict(x_test)
score = accuracy_score(y_test, y_predict)
print(f"Model Accuracy: {score * 100:.2f}% ({score})")

# save the trained model
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)