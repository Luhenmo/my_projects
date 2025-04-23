import matplotlib.pyplot as plt 
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from pathlib import Path
from copy import deepcopy
from utils.asset_database import DICT_ASSET_INFO
from data.historico_tesouro.tresury_history import DICT_TRESURY_HISTORY

### global variables ###
dict_asset = DICT_ASSET_INFO
PATH_MAIN_FOLDER = Path("c:/Users/luizh/Documentos/visual_studio/my_projects/investiment_control")

class_colors = {
    "total":("tab:grey",0.5),
    'USD':'tab:red',
    'Tesouro':'tab:green',
    'Ação': 'tab:blue',
    'FII': 'y',
}

month_names = {
    1:'Jan', 
    2:'Feb', 
    3:'Mar', 
    4:'Apr', 
    5:'May', 
    6:'Jun', 
    7:'Jul', 
    8:'Aug', 
    9:'Sep', 
    10:'Oct', 
    11:'Nov', 
    12:'Dec',
}

def generate_list_of_dates(months_amount:int,naive:bool=True):
    list_dates = [
        pd.Timestamp(2024,pd.Timestamp.today().month,1,tz=None if naive else 'America/Sao_Paulo')
        - relativedelta(months=months_amount-i-1) - pd.Timedelta(days=1)
        for i in range(months_amount)]
    list_dates.append(pd.Timestamp.today(tz=None if naive else 'America/Sao_Paulo'))
    return list_dates

def get_bond_value(
    bond_name:str,
    date:pd.Timestamp,
    )->float:

    if date == pd.Timestamp.today():
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
    date:pd.Timestamp,
    )->float:

    earlier = date - pd.Timedelta(days=7)
    value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    num = 1
    while (np.size(value) == 0) and (num < 4):
        date = date + pd.Timedelta(days=7)
        earlier = date - pd.Timedelta(days=7)
        value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
        num += 1
    if num == 4:
        return None
    else:
        value = value.sort_index(ascending=False).iloc[0].values[0]
        return np.round(value,2)

def get_us_stock_value(
        stock_name:str,
        date:pd.Timestamp,
        output_currency:str="BRL",
    )->float:

    earlier = date - pd.Timedelta(days=7)
    value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    while np.size(value) == 0:
        date = date + pd.Timedelta(days=7)
        earlier = date - pd.Timedelta(days=7)
        value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    value = value.sort_index(ascending=False).iloc[0].values[0]

    if output_currency == "BRL":
        usd_brl = yf.Ticker("BRL%3DX").history(start=earlier,end=date)[["Close"]]
        usd_brl = usd_brl.sort_index(ascending=False).iloc[0].values[0]
        value = value * usd_brl
    return np.round(value,2)

def get_value(
    asset_name:str,
    date:pd.Timestamp=pd.Timestamp.today(),
    )->float:
    if dict_asset[asset_name].stock_b3:
        return get_b3_stock_value(dict_asset[asset_name].ticker,date)
    if dict_asset[asset_name].stock_us:
        return get_us_stock_value(dict_asset[asset_name].ticker,date)
    if dict_asset[asset_name].bond:
        return get_bond_value(dict_asset[asset_name].ticker,date)

def get_position(
        data_base:pd.DataFrame,
        ticker:str,
        date:pd.Timestamp=pd.Timestamp.today(),
    )->tuple[float,float,float]:

    operation = data_base[(data_base["Ativo"] == ticker) & (data_base["Data"] <= date)]
    if np.size(operation) == 0:
        return 0,0,0

    is_first = True
    for index in operation.sort_values("Data").index:

        if is_first:
            medium_price = operation["Preço"][index]
            amount = operation["Qnt"][index]
            profit = 0

            is_first = False
        else:
            if operation["C/V"][index] == "C":

                medium_price = (medium_price * amount + operation["Preço"][index] * operation["Qnt"][index])/(amount + operation["Qnt"][index])
                amount += operation["Qnt"][index]
            else:
                amount -= operation["Qnt"][index]            
                profit += (operation["Preço"][index] - medium_price) * operation["Qnt"][index]

    return medium_price,amount,profit

def convert_to_currency(
        base_dados:pd.DataFrame,
        currency:str,
    ):

    data_final = base_dados["Data"].iloc[0] + pd.Timedelta(days=1)
    data_inicial = base_dados["Data"].iloc[-1]
 
    lista_moedas = ["USD","EUR","BRL"]
    lista_moedas.remove(currency)
    dic_historico_convercao = {}
    for moeda_inicial in lista_moedas:

        historico = yf.Ticker(f"{moeda_inicial}{currency}=X").history(start=data_inicial,end=data_final)[["Close"]]
        dic_historico_convercao.update({f"{moeda_inicial}_to_{currency}":historico})

    df = deepcopy(base_dados)
    def conversion_function(row):
        if row["Moeda"] != currency:
            moeda_atual = row["Moeda"]
            data = row["Data"]

            exchange_rate = dic_historico_convercao[
                f"{moeda_atual}_to_{currency}"
            ].asof(pd.Timestamp(data,tz="UTC"))["Close"]
            
        else:
            exchange_rate = 1
        return np.round(row["Preço"] * exchange_rate,2)
    df["Preço"] = df.apply(conversion_function, axis=1)
    df["Moeda"] = currency
    return df

def compute_position(            
    data_base:pd.DataFrame,
    date:pd.Timestamp=pd.Timestamp.today(),
    currency:str = "BRL"
    ) -> pd.DataFrame:
    
    ### Converte todas as entradas a mesma moeda
    data_base = convert_to_currency(data_base,currency)

    filtered_data_base = data_base[data_base["Data"] <= date]
    
    _mask_actual_position = [0 != get_position(filtered_data_base,ticker,date)[1] for ticker in filtered_data_base["Ativo"].unique()]


    _assets_in_actual_position = filtered_data_base["Ativo"].unique()[_mask_actual_position]

    position = pd.DataFrame({
        "Ativo":[ticker for ticker in _assets_in_actual_position],
        "Classe":[DICT_ASSET_INFO[ticker].asset_class for ticker in _assets_in_actual_position],
        "Qnt":[get_position(filtered_data_base,ticker,date)[1] for ticker in _assets_in_actual_position],
        "Custo unitário":[get_position(filtered_data_base,ticker,date)[0] for ticker in _assets_in_actual_position],
        "Preço unitário":[get_value(ticker,date) for ticker in _assets_in_actual_position],
    })

    position["Custo total"] = np.round(position["Custo unitário"] * position["Qnt"],2)
    position["Valor total"] = np.round(position["Preço unitário"] * position["Qnt"],2)
    
    position = position.sort_values(by=["Classe","Valor total"],ascending=[True,False])

    return position

def get_field_for_assets_in_position(position,assets,field):
    
    list_row = [position[position['Ativo'] == ativo][field].values for ativo in assets]
    return np.array([0 if x.size == 0  else x[0] for x in list_row])

def plot_position_graph(
        position:pd.DataFrame,
        plot_image:bool=True,
    )->None:

    def generate_colors(base_color, num_assets):
        cmap = plt.get_cmap(base_color)
        return [cmap((2*num_assets-i) / (3*num_assets)) for i in range(num_assets)]

    def label_with_revenue(class_value, total_value, title):
        pct = int(np.round(class_value/total_value*100))
        return f"{title}\nR${int(class_value)}\n({pct:.1f}%)"

    def autopct_with_revenue(pct, allvalues):
        absolute = int(np.round(pct/100.*np.sum(allvalues)))
        # return f"R${absolute}\n({pct:.1f}%)"
        return f"R${absolute} ({pct:.1f}%)"
    
    # Adjust the position of each percentage text
    def change_label_radial_distance(list_distances,text_to_modify,wedges):
        for i, text in enumerate(text_to_modify):
            angle = (wedges[i].theta2 - wedges[i].theta1) / 2. + wedges[i].theta1
            x = list_distances[i%len(list_distances)] * np.cos(np.deg2rad(angle))
            y = list_distances[i%len(list_distances)] * np.sin(np.deg2rad(angle))
            text.set_position((x, y))

    # Define color maps for each class
    class_colors = {
        'USD': 'Reds',
        'Tesouro': 'Greens',
        'Ação': 'Blues',
        'FII': 'Purples',
    }

    unique_classes = position["Classe"].unique()
    class_store_counts = {cls: (position["Classe"] == cls).sum() for cls in unique_classes}
    class_colors_tones = {cls: generate_colors(class_colors[cls], count) for cls, count in class_store_counts.items()}

    store_colors = []
    class_color_index = {cls: 0 for cls in unique_classes}

    for cls in position["Classe"]:
        store_colors.append(class_colors_tones[cls][class_color_index[cls]])
        class_color_index[cls] += 1

    pct_distances = [0.90,0.7]
    width_chart_1 = 0.4
    font_size_chart_1 = 10

    fig, ax = plt.subplots(figsize=(10, 10))
    wedges, texts, autotexts = ax.pie(
        position["Preço unitário"]*position["Qnt"], 
        labels=position["Ativo"], 
        colors=store_colors, 
        autopct=lambda pct: autopct_with_revenue(pct, position["Valor total"]), 
        startangle=90,
        # pctdistance=0.9,
        wedgeprops=dict(width=width_chart_1, edgecolor='w'),
        textprops={'fontsize': font_size_chart_1},
    )

    change_label_radial_distance(pct_distances,autotexts,wedges)

    label_distance = 0.43
    width_chart_2 = 0.3
    font_size_chart_2 = 16
    
    wedges_2, texts_2 = ax.pie(
        [position[position["Classe"] == classe]["Valor total"].sum() 
            for classe in unique_classes],
        startangle=90,
        radius=1-width_chart_1, 
        colors=[plt.get_cmap(class_colors[classe])(0.55) for classe in unique_classes],
        wedgeprops=dict(width=width_chart_2, edgecolor='w'),
        labels=[
            label_with_revenue(position[position["Classe"] == classe]["Valor total"].sum()
            ,position["Valor total"].sum(), classe) for classe in unique_classes],
        textprops = {
            'fontsize': font_size_chart_2,
            'fontweight': 'bold',
            'ha': 'center','va': 'center'
        }
    )

    change_label_radial_distance([label_distance],texts_2,wedges_2)

    ax.axis('equal')
    # ax.set_title(f'Assets in {date.strftime("%d/%m/%y")}',ha='center',va='bottom',fontweight='bold',bbox=dict(boxstyle="round",ec=("gray", 0.5),fc=("gray", 0.3)))

    ax.text(
    0.05, 1, f'Payed price\nR${np.round(position["Custo total"].sum(),2)}', transform=plt.gca().transAxes,
    fontsize=20, fontweight='bold', ha='center',va='center', bbox=dict(boxstyle="round",fc=("tab:blue", 0.5),ec=("tab:blue", 1))
    )

    ax.text(
        0.95,1, f'Actual price\nR${np.round(position["Valor total"].sum(),2)}', transform=plt.gca().transAxes,
        fontsize=20, fontweight='bold', ha='center',va='center', bbox=dict(boxstyle="round",fc=("tab:red", 0.5),ec=("tab:red", 1))
    )

    # if save_image:
    #     plt.savefig(PATH_MAIN_FOLDER / "images" / f"position_{data_base["Dono"]}_{date.strftime("%y-%m-%d")}.png") 
    if plot_image:
        plt.show()
    else:
        return fig

def plot_position_table(
        data_base:pd.DataFrame,
        date:pd.Timestamp = pd.Timestamp.today(),
        save_image:bool=False,
        plot_image:bool=True,
    )->None:

    actual = compute_position(data_base,date=date)      
    # Calculate the Absolute Difference and Percentage Difference
    actual['Difference'] = np.round(actual["Valor total"] - actual['Total cost'],2)
    actual['Percentage'] = np.round((actual['Difference'] / actual['Total cost']) * 100,2)

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 7)) # Adjust the size as needed
    ax.axis('off')

    ax.text(
        0.5, 1, f'Posição em {date.strftime("%d/%m/%y")}', transform=plt.gca().transAxes,
        fontsize=12, fontweight='bold', ha='center',va='center', bbox=dict(boxstyle="round",fc=("tab:blue", 0.5),ec=("tab:blue", 1))
    )

    # Create the table
    ax.text
    table = ax.table(
        cellText=actual.drop(["Classe", "Custo unitário","Preço unitário"],axis=1).values,
        colLabels=["Nome","Qnt","Custo","Preço","Lucro","Porcentagem"],
        cellLoc='center',
        loc=(0.5,0)
    )

    # Apply the color function to the percentage difference column
    for i, percentage in enumerate(actual['Percentage']):
        table[(i+1, 5)].set_text_props(color='green' if percentage > 0 else 'red')


    if save_image:
        plt.savefig(PATH_MAIN_FOLDER / "images" / f"table_{data_base["Dono"]}_{date.strftime("%y-%m-%d")}.png") 
    if plot_image:
        plt.show()

def plot_earnings_in_last_months(
        portifolio:pd.DataFrame,
        delta_months:int,
        save_image:bool=False,
        plot_image:bool=True,
    )->None:

    data_base = portifolio.data_base
        
    list_dates = generate_list_of_dates(delta_months)

    dict_positions = {
        date:compute_position(data_base,date=date)[0] for date in list_dates
    }

    bar_width = 0.2
    x = np.arange(len(list_dates)-1)

    # Create the plot
    fig, ax = plt.subplots()

    for i,_class in enumerate(class_colors.keys()):
        if _class == "total":
            total_per_month = [dict_positions[date]["Valor total"].sum() for date in dict_positions.keys()]     
            earnings_per_month = [total_per_month[i+1] - total_per_month[i] for i in range(len(total_per_month)-1)]

            bars = ax.bar(
                x+2*bar_width,
                earnings_per_month, 
                color=[class_colors[_class] for x in earnings_per_month],
                width=4*bar_width,
                label=f"{_class}"
            )

        else:
            total_per_month = [dict_positions[date][dict_positions[date]["Classe"] == _class]["Valor total"].sum() for date in dict_positions.keys()] 
            earnings_per_month = [total_per_month[i+1] - total_per_month[i] for i in range(len(total_per_month)-1)]

            bars = ax.bar(
                x + bar_width/2 + (i-1) * bar_width,
                earnings_per_month, 
                color=[class_colors[_class] for x in earnings_per_month],
                width=bar_width,
                label=f"{_class}"
            )

    # Draw a central line at y=0
    ax.axhline(0, color='black', linewidth=0.8)

    # Add labels and title
    ax.set_xticks(x + bar_width * (len(class_colors) - 1) / 2)
    ax.set_xticklabels([month_names[month_num.month] for month_num in list_dates[1:]])
    ax.set_ylabel('Earnings/Losses (BRL)')
    ax.set_xlabel('Month')
    ax.set_title(f'{portifolio.owner} monthly changes in the last {delta_months} months ({pd.Timestamp.today().strftime("%y-%m-%d")})')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Show the plot
    if save_image:
        plt.savefig(PATH_MAIN_FOLDER / "images" / f"earning_{portifolio.owner}.png") 
    if plot_image:
        plt.show()

def compute_dividends(
        data_base:pd.DataFrame,
    )->pd.DataFrame:

    data_base["Classe"] = [DICT_ASSET_INFO[ativo].asset_class for ativo in data_base["Ativo"]]

    df = data_base[data_base["Classe"] != "Tesouro"]
    dividens_data_base = pd.DataFrame(columns=["Data","Ativo","Classe","Dividendo","Qnt","Dividendo total"])

    for ticker in df["Ativo"].unique():
        dividend_data = yf.Ticker(DICT_ASSET_INFO[ticker].ticker).dividends
        for dividend_date,dividend in zip(dividend_data.index,dividend_data):
            date = pd.Timestamp(dividend_date.year,dividend_date.month,dividend_date.day)
            position_in_date = get_position(
                data_base=df,
                ticker=ticker,
                date=date,
            )[1]
            if position_in_date > 0:

                dict_dividend = {
                    "Data":dividend_date,
                    "Ativo":ticker,
                    "Classe":DICT_ASSET_INFO[ticker].asset_class,
                    "Dividendo":dividend,
                    "Qnt":position_in_date,
                    "Dividendo total":position_in_date * dividend,
                }

                if DICT_ASSET_INFO[ticker].asset_class == "USD":

                    earlier = date - pd.Timedelta(days=7)
                    usd_brl = yf.Ticker("BRL%3DX").history(start=earlier,end=date)[["Close"]]
                    usd_brl = usd_brl.sort_index(ascending=False).iloc[0].values[0]
                    dict_dividend["Dividendo"] = np.round(dict_dividend["Dividendo"] * usd_brl,2)
                    dict_dividend["Dividendo total"] = np.round(dict_dividend["Dividendo total"] * usd_brl,2)

                dividens_data_base.loc[len(dividens_data_base)] = dict_dividend

    dividens_data_base["Data"] = pd.to_datetime(dividens_data_base["Data"], utc=True).dt.date
    dividens_data_base =  dividens_data_base.sort_values(by="Data",ignore_index=True)
    return dividens_data_base

def plot_dividends_in_last_months(        
        portifolio:pd.DataFrame,
        delta_months:int,
        save_image:bool=False,
        plot_image:bool=True,
    )->None:

    dividens = compute_dividends(portifolio)
    list_dates = generate_list_of_dates(delta_months,naive=False)

    # Create the plot
    fig, ax = plt.subplots()
    # Calculate bottom positions for stacking
    bottoms = np.zeros(delta_months)

    for asset_class in dividens["classe"].unique():
        earnings_per_month = [
                dividens[
                    (dividens["date"] > frist_day_of_the_month) & 
                    (dividens["date"] <= last_day_of_the_month) &
                    (dividens["classe"] == asset_class)
                ]["total_dividend"].sum() 
                for frist_day_of_the_month,last_day_of_the_month in zip(list_dates[:len(list_dates)-1],list_dates[1:])
            ]
        
        bars = ax.bar(
            [month_names[date.month] for date in list_dates[1:]],
            earnings_per_month,
            bottom = bottoms,
            color = class_colors[asset_class],
            label = asset_class,
        )
        bottoms += earnings_per_month

    # Add labels and title
    ax.set_ylabel('Earnings/Losses (BRL)')
    ax.set_xlabel('Month')
    ax.set_title(f'{portifolio.owner} monthly dividends in the last {delta_months} months ({pd.Timestamp.today().strftime("%y-%m-%d")})')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Show the plot
    if save_image:
        plt.savefig(PATH_MAIN_FOLDER / "images" / f"dividends_{portifolio.owner}.png")
    if plot_image:
        plt.show()
