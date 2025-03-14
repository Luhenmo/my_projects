from pathlib import Path
import os
import pandas as pd
import requests
from datetime import datetime,timedelta

### functions ###

def update_last_download_time(last_update_path):
    with open(last_update_path, 'w') as file:
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def should_download(last_update_path, threshold_hours=24):
    if not os.path.exists(last_update_path):
        return True

    with open(last_update_path, 'r') as file:
        last_download_str = file.read().strip()
    last_update_path = datetime.strptime(last_download_str, '%Y-%m-%d %H:%M:%S')
    return (datetime.now() - last_update_path) > timedelta(hours=threshold_hours)

### variables ###

current_path = Path(os.path.dirname(os.path.abspath(__file__)))
last_update_path = current_path / "last_update.txt"

years = [2025]#[2023,2024,2025]

bond_names = {
    "IPCA+ 2029":"NTN-B Princ 150529",
    "IPCA+ 2045":"NTN-B Princ 150545",
    "IPCA+ 2050":"NTN-B Princ 150850",
    "Selic 2026":"LFT 010326",
    "Selic 2029":"LFT 010329",
    "Prefixado 2029":"LTN 010129",
} 

bond_types = {
    "IPCA+ 2029":"IPCA+",
    "IPCA+ 2045":"IPCA+",
    "IPCA+ 2050":"IPCA+",
    "Selic 2026":"Selic",
    "Selic 2029":"Selic",
    "Prefixado 2029":"Prefixado",
}

spread_sheet_names = {
    "Prefixado":"LTN",
    "Selic":"LFT",
    "IPCA+":"NTN-B_Principal",
}

### main ###

update = should_download(last_update_path)

if update:
    update_last_download_time(last_update_path)

    for file_name in spread_sheet_names.values():
        response = requests.get(f"https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/2025/{file_name}_2025.xls")
        write_path = current_path / f"{file_name}_2025.xls"

        with open(write_path, 'wb') as file:
            file.write(response.content)

DICT_TRESURY_HISTORY = {name:pd.DataFrame(columns=[["Dia","Taxa","Preço"]]) for name in bond_names.keys()}

for name,sheet_name in bond_names.items():
    for year in years:
        df = pd.read_excel(current_path / f"{spread_sheet_names[bond_types[name]]}_{year}.xls", sheet_name=sheet_name)
        df.columns = df.loc[0]
        df = df.drop([0],axis=0)
        df = df.drop(["Taxa Compra Manhã","PU Compra Manhã","PU Venda Manhã"],axis=1)
        df = df.rename(columns={"Taxa Venda Manhã":"Taxa","PU Base Manhã":"Preço"})
        df["Dia"] = df["Dia"].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
        if len(DICT_TRESURY_HISTORY[name]) == 0:
            DICT_TRESURY_HISTORY[name] = df
        else:
            DICT_TRESURY_HISTORY[name] = pd.concat([DICT_TRESURY_HISTORY[name],df],axis=0,ignore_index=True)
