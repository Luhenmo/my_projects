from dataclasses import dataclass
from asset_database import DICT_ASSET_INFO
from tools import get_value
import pandas as pd
import numpy as np


@dataclass
class Portfolio:
    data_base:pd.DataFrame

    def __post_init__(self):
        self.data_base["class"] = [DICT_ASSET_INFO[ticker].asset_class for ticker in self.data_base["ticker"]]


##### unused #####
@dataclass
class Transaction:
    owner:str
    date:pd.Timestamp
    ticker:str
    buy:bool
    price:float
    amount:int
    curency:str="BRL"








