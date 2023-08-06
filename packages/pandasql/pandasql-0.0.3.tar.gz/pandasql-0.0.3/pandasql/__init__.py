from sqldf import sqldf
import os
import pandas as pd


_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_data(path):
    return os.path.join(_ROOT, 'data', path)

def load_meat():
    import pandas as pd
    filename = get_data("meat.csv")
    return pd.read_csv(filename, parse_dates=[0])

def load_births():
    import pandas as pd
    filename = get_data("births_by_month.csv")
    return pd.read_csv(filename, parse_dates=[0])

