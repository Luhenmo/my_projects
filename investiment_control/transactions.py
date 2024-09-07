from classes import Transaction
import pandas as pd

LIST_TRANSACTIONS = [
    Transaction(
        owner="Luiz",
        date=pd.Timestamp(2024,8,20),
        ticker=["CSMG3","GGBR4","VALE3","AFHI11"],
        buy=[True,True,True,True],
        price=[23.22,17.57,57.14,96.64],
        amount=[8,11,4,6],
    ),
    Transaction(
        owner="Luiz",
        date=pd.Timestamp(2024,8,7),
        ticker=["ITSA4","RAIZ4","BBAS3","CSMG3","ICRI11","HGRE11"],
        buy=[True,True,True,True,True,True],
        price=[9.96,3.06,26.43,21.79,97.19,113.84],
        amount=[19,66,8,14,9,8],
    ),
    Transaction(
        owner="Luciane",
        date=pd.Timestamp(2024,8,7),
        ticker=["Selic 2029","TRXF11","HGLG11","ALZR11","KNSC11","HSML11","HGRU11","KNIP11","HGRE11","ICRI11"],
        buy=[False,False,False,False,False,False,True,True,True,True],
        price=[15072.74,105.08,160.10,108.20,9.17,95.50,127.02,94.30,113.70,96.92],
        amount=[0.11,17,9,18,218,20,16,21,18,21],
    ),   
    Transaction(
        owner="Luciane",
        date=pd.Timestamp(2024,8,13),
        ticker=["ALUG11"],
        buy=[False],
        price=[40.85],
        amount=[30],
    ),  
]