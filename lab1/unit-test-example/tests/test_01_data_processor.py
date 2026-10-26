import json
import os

import pandas as pd
import pytest

from src.simple_data_processor import SimpleDataProcessor


class TestDiabetesPredictor:
    def test_process_correct_data(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_file = os.path.join(test_dir, "../testResources/test_dataset_correct.json")
        dp = SimpleDataProcessor()
        x,y = dp.process(test_data_file)
        assert x is not None
        assert y is not None
        assert x.shape[0] == y.shape[0]
        assert x.shape[1] == 8
        assert x.size == 24
        assert y.size == 3

    def test_process_incorrect_data(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_file = os.path.join(test_dir, "../testResources/test_dataset_incorrect_1.json")
        dp = SimpleDataProcessor()
        with pytest.raises(ValueError) as e_info:
            dp.process(test_data_file)
        assert '9 columns.' in str(e_info)
        test_data_file = os.path.join(test_dir, "../testResources/test_dataset_incorrect_2.json")
        with pytest.raises(ValueError) as e_info:
            dp.process(test_data_file)
        assert 'a class variable as the last column.' in str(e_info)