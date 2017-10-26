import pandas as pd
import json
from pprint import pprint

def read_csv(file):
        data_frame = pd.read_csv(file)
        return data_frame

def read_json(file):
        with open(file) as data_file:
                data = json.load(data_file)
        return data
