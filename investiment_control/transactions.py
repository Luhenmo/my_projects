import pandas as pd
from pathlib import Path
from datetime import datetime


current_path = Path.cwd()
csv_name = "investimentos_movimentacoes.csv"
raw_data = pd.read_csv(filepath_or_buffer=current_path/csv_name)
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

#### Add more ransactions using 


####

GLOBAL_DATA_BASE = data_base