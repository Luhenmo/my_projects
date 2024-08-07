from dataclasses import dataclass
from asset_database import DICT_ASSET_INFO
import pandas as pd
import numpy as np


@dataclass
class Portfolio:
    data_base:pd.DataFrame
    owner:str

    def __post_init__(self):
        self.data_base["class"] = [DICT_ASSET_INFO[ticker].asset_class for ticker in self.data_base["ticker"]]

class Transaction:
    def __init__(
            self,
            owner:str,
            date:pd.Timestamp,
            ticker:list[str],
            buy:list[bool],
            price:list[float],
            amount:list[int],
            curency:list[str]=["BRL"],
        )->None:
        self.owner=owner
        self.date=date
        self.ticker=ticker
        self.buy=buy
        self.price=price
        self.amount=amount
        self.curency=curency








