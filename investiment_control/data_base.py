import pandas as pd
from pathlib import Path
from datetime import datetime
from tools import add_transaction
from transactions import LIST_TRANSACTIONS

PATH_MAIN_FOLDER = Path("c:/Users/luizh/Documents/visual_studio/my_projects/investiment_control")

csv_name = "investimentos_movimentacoes.csv"
raw_data = pd.read_csv(filepath_or_buffer=PATH_MAIN_FOLDER/csv_name)
list_to_pop = ["Lucro","Imposto","Observação","F sup","Preço médio","Valor total"]
for name in list_to_pop:
    raw_data.pop(name)

data_base = pd.DataFrame()
data_base["owner"] = raw_data["Banco"].apply(lambda text: "Luiz" if text =="Inter" else "Luciane")
data_base["date"] = raw_data["Data operação"].apply(lambda date: datetime.strptime(date,"%d/%m/%Y"))
data_base["ticker"] = raw_data["Nome ativo"]
data_base["buy"] = raw_data["C/V"].apply(lambda text: True if text=="C" else False)
data_base["price"] = raw_data["Preço operação"].apply(lambda price_text: float(''.join(filter(lambda x: x.isdigit() or x in ',', price_text)).replace(",",".")))
data_base["amount"] = raw_data["Qnt"].apply(lambda Qnt: float(Qnt.replace(",",".")))
data_base["curency"] = "BRL"

for transaction in LIST_TRANSACTIONS[::-1]:
    data_base = add_transaction(
        data_base=data_base,
        transaction=transaction,
    )

GLOBAL_DATA_BASE = data_base