from pathlib import Path
import os
import pandas as pd
import requests
from datetime import datetime,timedelta

current_path = Path(os.path.dirname(os.path.abspath(__file__)))
last_update_path = current_path / "last_update.txt"

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

update = should_download(last_update_path)

if update:
    update_last_download_time(last_update_path)

    IPCA_file_name = "NTN-B_Principal_2024.xls"
    selic_file_name = "LFT_2024.xls"

    url_IPCA_2024 = "https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/2024/NTN-B_Principal_2024.xls"
    url_selic_2024 = "https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/2024/LFT_2024.xls"

    files_to_import = {
        IPCA_file_name:url_IPCA_2024,
        selic_file_name:url_selic_2024,
    }

    for file_name,url in files_to_import.items():
        response = requests.get(url)
        write_path = current_path / file_name

        with open(write_path, 'wb') as file:
            file.write(response.content)

bond_names = {
    "IPCA+ 2029":"NTN-B Princ 150529",
    "IPCA+ 2045":"NTN-B Princ 150545",
}

DICT_TRESURY_HISTORY = {name:pd.DataFrame(columns=[["Dia","Taxa","Preço"]]) for name in bond_names.keys()}

# for sheet_name in bond_names.values():
for name,sheet_name in bond_names.items():
    for year in [2023,2024]:
        df = pd.read_excel(current_path / f"NTN-B_principal_{year}.xls", sheet_name=sheet_name)
        df.columns = df.loc[0]
        df = df.drop([0],axis=0)
        df = df.drop(["Taxa Compra Manhã","PU Compra Manhã","PU Venda Manhã"],axis=1)
        df = df.rename(columns={"Taxa Venda Manhã":"Taxa","PU Base Manhã":"Preço"})
        df["Dia"] = df["Dia"].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
        if len(DICT_TRESURY_HISTORY[name]) == 0:
            DICT_TRESURY_HISTORY[name] = df
        else:
            DICT_TRESURY_HISTORY[name] = pd.concat([DICT_TRESURY_HISTORY[name],df],axis=0,ignore_index=True)


bond_names = {
    "Selic 2029":"LFT 010329"
} 

DICT_TRESURY_HISTORY.update({name:pd.DataFrame(columns=[["Dia","Taxa","Preço"]]) for name in bond_names.keys()})

for name,sheet_name in bond_names.items():
    for year in [2023,2024]:
        df = pd.read_excel(current_path / f"LFT_{year}.xls",sheet_name=sheet_name)
        df.columns = df.loc[0]
        df = df.drop([0],axis=0)
        df = df.drop(["Taxa Compra Manhã","PU Compra Manhã","PU Venda Manhã"],axis=1)
        df = df.rename(columns={"Taxa Venda Manhã":"Taxa","PU Base Manhã":"Preço"})
        df["Dia"] = df["Dia"].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
        if len(DICT_TRESURY_HISTORY[name]) == 0:
            DICT_TRESURY_HISTORY[name] = df
        else:
            DICT_TRESURY_HISTORY[name] = pd.concat([DICT_TRESURY_HISTORY[name],df],axis=0,ignore_index=True)
