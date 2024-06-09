from dataclasses import dataclass
from datetime import date


@dataclass
class AssetInfo:
    name:str
    ticker:str
    asset_class:str
    stock_b3:bool=False
    stock_us:bool=False
    bond:bool=False

@dataclass
class Transaction:
    owner:str
    date:date
    ticker:str
    buy:bool
    price:float
    amount:int
    curency:str="BRL"

@dataclass
class Position:
    owner:str
    date:date
    ticker:str
    buy:bool
    price:float
    amount:int
    curency:str="BRL"







