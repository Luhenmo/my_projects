
from datetime import datetime,timedelta
from datetime import date
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from asset_database import DICT_ASSET_INFO
from historico_tesouro.tresury_history import DICT_TRESURY_HISTORY

dict_asset = DICT_ASSET_INFO

def get_bond_value(
    bond_name:str,
    date:datetime,
    )->float:

    if date == datetime.today():
        bond_name = ("Tesouro"+bond_name).lower().replace(" ","")
        # Define the URL
        url = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json"
        response = requests.get(url)
        for _dict in response.json()["response"]["TrsrBdTradgList"]:
            if _dict["TrsrBd"]["nm"].lower().replace(" ","") == bond_name:
                return float(_dict["TrsrBd"]["untrRedVal"])
    else:
        return float(
            DICT_TRESURY_HISTORY[bond_name][
                DICT_TRESURY_HISTORY[bond_name]["Dia"] < date
            ].sort_values(by="Dia",ascending=False)["Preço"].iloc[0])

def get_b3_stock_value(
    stock_name:str,
    date,
    )->float:

    now = datetime.today()
    earlier = now - timedelta(days=1)
    value = yf.Ticker(stock_name).history(start=earlier,end=now)[["Close"]]
    value = float(*value["Close"].values)
    return np.round(value,2)

def get_us_stock_value(
        stock_name:str,
        output_currency:str="BRL",
    )->float:

    now = datetime.today()
    earlier = now - timedelta(days=1)
    value = yf.Ticker(stock_name).history(start=earlier,end=now)[["Close"]]
    value = float(*value["Close"].values)

    if output_currency != "USD":
        usd_brl = yf.Ticker("BRL%3DX").history(start=earlier,end=now)[["Close"]]
        usd_brl = float(*usd_brl["Close"].values)
        value = value * usd_brl
    return np.round(value,2)

def get_value(
    asset_name:str,
    date:datetime=datetime.today(),
    )->float:
    if dict_asset[asset_name].stock_b3:
        return get_b3_stock_value(dict_asset[asset_name].ticker)
    if dict_asset[asset_name].stock_us:
        return get_us_stock_value(dict_asset[asset_name].ticker)
    if dict_asset[asset_name].bond:
        return get_bond_value(dict_asset[asset_name].ticker,date)



