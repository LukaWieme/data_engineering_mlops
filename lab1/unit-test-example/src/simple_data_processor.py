import json

import pandas as pd


class SimpleDataProcessor:

    def process(self, dataset_json_file):
        """
           Take a dataset in json and return features and class variable

           Args:
               dataset_json_file (string): dataset file name.
           Returns:
               X: features
               Y: class
           """
        dataset = pd.read_json(dataset_json_file, orient='records')
        columns = dataset.columns.values
        if len(columns) != 9:
            raise ValueError('The dataset must have 9 columns.')
        if columns[8] != 'class':
            raise ValueError('The dataset must have a class variable as the last column.')
        data = dataset.values
        # split into input (X) and output (Y) variables
        X = data[:, 0:8]
        Y = data[:, 8]
        return X, Y
