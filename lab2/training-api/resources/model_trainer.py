# A simple DecisionTreeClassifier for Pima Indians Dataset saved to single file
# see https://www.kaggle.com/datasets/jamaltariqcheema/pima-indians-diabetes-dataset/
import logging
import os
from pathlib import Path

from flask import jsonify
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score
from sklearn.tree import DecisionTreeClassifier


def train(dataset):
    # split into input (X) and output (Y) variables
    X = dataset[:, 0:8]
    Y = dataset[:, 8]
    train_X, val_X, train_y, val_y = train_test_split(X, Y, random_state=42)
    model = DecisionTreeClassifier(criterion="gini", random_state=42)
    # Fit the model
    model.fit(train_X, train_y)
    val_predictions = model.predict(val_X)
    accuracy = accuracy_score(val_y, val_predictions)
    recall = recall_score(val_y, val_predictions)
    print(f"Accuracy:{accuracy:.3f} | Recall:{recall:.3f}")
    # evaluate the model
    text_out = {
        "accuracy:": accuracy,
        "recall": recall,
    }
    logging.info(text_out)
    # Saving model in a given location provided as an env. variable
    model_repo = os.getenv('MODEL_REPO')
    if model_repo:
        Path(model_repo).mkdir(parents=True, exist_ok=True)  # Create if it does not exist
        file_path = os.path.join(model_repo, "model.pkl")
        # save object to pickle file
        with open(file_path, 'wb') as f:
            pickle.dump(model, f)
        logging.info("Saved the model to the location : " + model_repo)
        return jsonify(text_out), 200
    else:
        # Otherwise, save the model locally
        with open("model.pkl", 'wb') as f:
            pickle.dump(model, f)
        return jsonify({'message': 'The model was saved locally.'}), 200
