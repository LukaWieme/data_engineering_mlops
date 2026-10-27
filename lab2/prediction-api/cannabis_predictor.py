import json
import os

import pandas as pd
from flask import jsonify
import logging
from io import StringIO
import pickle


SCORE_MAPS = {
    "Nscore": {15: -2.52197,
               20: -2.21844,
               25: -1.19430,
               30: -0.58016,
               35: -0.05188,
               40: 0.41667,
               45: 0.91093,
               50: 1.49158,
               55: 2.12700,
               60: 3.27393},
    "Escore": {15: -3.27393,
               20: -2.53830,
               25: -2.03972,
               30: -1.37639,
               35: -0.69509,
               40: 0.00332,
               45: 0.80523,
               50: 1.58487,
               55: 2.57309,
               60: 3.27393},
    "Oscore": {15: -3.27393,
               20: -3.27393,
               25: -2.85950,
               30: -2.21069,
               35: -1.55521,
               40: -0.84732,
               45: -0.17779,
               50: 0.58331,
               55: 1.43533,
               60: 2.90161},
    "Ascore": {15: -3.15735,
               20: -3.00537,
               25: -2.70172,
               30: -1.92595,
               35: -1.21213,
               40: -0.45321,
               45: 0.28783,
               50: 1.11406,
               55: 2.03972,
               60: 3.46436},
    "Cscore": {15: -3.46436,
               20: -2.90161,
               25: -2.18109,
               30: -1.54840,
               35: -0.89891,
               40: -0.27607,
               45: 0.41594,
               50: 1.30612,
               55: 2.33337,
               60: 3.46436},
    "Impulsive": {1: -2.55524,
                  2: -1.37983,
                  3: -0.71126,
                  4: -0.21712,
                  5: 0.19268,
                  6: 0.52975,
                  7: 0.88113,
                  8: 1.29221,
                  9: 1.86203,
                  10: 2.90161},
    "SS": {1: -2.07848,
           2: -1.54858,
           3: -1.18084,
           4: -0.84637,
           5: -0.52593,
           6: -0.21575,
           7: 0.07987,
           8: 0.40148,
           9: 0.76540,
           10: 1.22470,
           11: 1.92173}
}


def get_nearest_score(raw_score, score_map):
    nearest_raw = min(
        score_map.keys(),
        key=lambda score: abs(score - raw_score)
    )
    return score_map[nearest_raw]

class DiabetesPredictor:
    def __init__(self):
        self.model = None

    def predict_single_record(self, prediction_input):
        logging.debug(prediction_input)
        if self.model is None:
            try:
                # load the model from a directory /folder given in the environment variables MODEL_REPO
                # assume the model file name as model.pkl
                model_repo = os.environ['MODEL_REPO']
                file_path = os.path.join(model_repo, "model.pkl")
                self.load_model(file_path)
            except KeyError:
                print("MODEL_REPO is undefined")
                # Otherwise, use the local model (in prediction-api folder)
                self.load_model('model.pkl')

        df = pd.read_json(StringIO(json.dumps(prediction_input)), orient='records')
        df = df.astype(float)
        for score, score_map in SCORE_MAPS.items():
            if score_map:
                raw_score = float(df.loc[0, score])
                df.loc[0, score] = get_nearest_score(raw_score, score_map)
        xNew = df[['Age', 'Gender', 'Education', 'Country', 'Ethnicity', 'Nscore', 'Escore', 'Oscore', 'Ascore',
                   'Cscore', 'Impulsive', 'SS']]
        y_pred = self.model.predict(xNew)
        print(y_pred)
        logging.info(y_pred[0])
        status = (y_pred[0])
        print(status)
        return status

    def load_model(self, file_path):
        self.model = pickle.load(open(file_path, 'rb'))
