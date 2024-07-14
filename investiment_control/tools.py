import matplotlib.pyplot as plt 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
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
    date:datetime,
    )->float:

    earlier = date - timedelta(days=7)
    value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    while np.size(value) == 0:
        date = date + timedelta(days=7)
        earlier = date - timedelta(days=7)
        value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    value = value.sort_index(ascending=False).iloc[0].values[0]
    return np.round(value,2)

def get_us_stock_value(
        stock_name:str,
        date:datetime,
        output_currency:str="BRL",
    )->float:

    earlier = date - timedelta(days=7)
    value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    while np.size(value) == 0:
        date = date + timedelta(days=7)
        earlier = date - timedelta(days=7)
        value = yf.Ticker(stock_name).history(start=earlier,end=date)[["Close"]]
    value = value.sort_index(ascending=False).iloc[0].values[0]

    if output_currency == "BRL":
        usd_brl = yf.Ticker("BRL%3DX").history(start=earlier,end=date)[["Close"]]
        usd_brl = usd_brl.sort_index(ascending=False).iloc[0].values[0]
        value = value * usd_brl
    return np.round(value,2)

def get_value(
    asset_name:str,
    date:datetime=datetime.today(),
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
        date:datetime=datetime.today(),
    )->tuple[float,float,float]:

    operation = data_base[(data_base["ticker"] == ticker) & (data_base["date"] <= date)]
    if np.size(operation) == 0:
        return 0,0,0

    is_first = True
    for index in operation.sort_values("date").index:
        if is_first:
            medium_price = operation["price"][index]
            amount = operation["amount"][index]
            profit = 0

            is_first = False
        else:
            if operation["buy"][index]:

                medium_price = (medium_price * amount + operation["price"][index] * operation["amount"][index])/(amount + operation["amount"][index])
                amount += operation["amount"][index]
            else:
                amount -= operation["amount"][index]            
                profit += (operation["price"][index] - medium_price) * operation["price"][index]

    return medium_price,np.round(amount,2),profit

def compute_position(            
    data_base:pd.DataFrame,
    date:datetime=datetime.today(),
    ) -> tuple[pd.DataFrame,pd.DataFrame]:
    
    filtered_data_base = data_base[data_base["date"] <= date]
    
    _mask_actual_position = [0 != get_position(filtered_data_base,ticker,date)[1] for ticker in filtered_data_base["ticker"].unique()]
    _mask_old_assets = [0 == get_position(filtered_data_base,ticker,date)[1] for ticker in filtered_data_base["ticker"].unique()]

    _assets_in_actual_position = filtered_data_base["ticker"].unique()[_mask_actual_position]
    _assets_in_old_assets = filtered_data_base["ticker"].unique()[_mask_old_assets]

    position = pd.DataFrame({
        "Ticker":[DICT_ASSET_INFO[ticker].name for ticker in _assets_in_actual_position],
        "Class":[DICT_ASSET_INFO[ticker].asset_class for ticker in _assets_in_actual_position],
        "Amount":[get_position(filtered_data_base,ticker,date)[1] for ticker in _assets_in_actual_position],
        "Cost per unit":[get_position(filtered_data_base,ticker,date)[0] for ticker in _assets_in_actual_position],
        "Price per unit":[get_value(ticker,date) for ticker in _assets_in_actual_position],
    })

    old_assets = pd.DataFrame({
        "Ticker":[DICT_ASSET_INFO[ticker].name for ticker in _assets_in_old_assets],
        "Class":[DICT_ASSET_INFO[ticker].asset_class for ticker in _assets_in_old_assets],
        "Amount":[get_position(filtered_data_base,ticker,date)[1] for ticker in _assets_in_old_assets],
        "Cost per unit":[get_position(filtered_data_base,ticker,date)[0] for ticker in _assets_in_old_assets],
        "Price per unit":[get_value(ticker,date) for ticker in _assets_in_old_assets],
    })

    position["Total cost"] = position["Cost per unit"] * position["Amount"]
    position["Total price"] = position["Price per unit"] * position["Amount"]
    
    position = position.sort_values(by=["Class","Total price"],ascending=[True,False])
    old_assets = old_assets.sort_values("Class")

    return position,old_assets

def plot_actual_postion(position)->None:

    def generate_colors(base_color, num_assets):
        cmap = plt.get_cmap(base_color)
        return [cmap((2*num_assets-i) / (3*num_assets)) for i in range(num_assets)]

    def autopct_with_revenue(pct, allvalues):
        absolute = int(np.round(pct/100.*np.sum(allvalues)))
        return f"R${absolute}\n({pct:.1f}%)"

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
        "Reserve": 'Greys',
    }

    unique_classes = position["Class"].unique()
    class_store_counts = {cls: (position["Class"] == cls).sum() for cls in unique_classes}
    class_colors_tones = {cls: generate_colors(class_colors[cls], count) for cls, count in class_store_counts.items()}

    store_colors = []
    class_color_index = {cls: 0 for cls in unique_classes}

    for cls in position["Class"]:
        store_colors.append(class_colors_tones[cls][class_color_index[cls]])
        class_color_index[cls] += 1

    pct_distances = [0.9,0.70]
    width_chart_1 = 0.4

    fig, ax = plt.subplots(figsize=(12,8))
    wedges, texts, autotexts = ax.pie(
        position["Price per unit"]*position["Amount"], 
        labels=position["Ticker"], 
        colors=store_colors, 
        autopct=lambda pct: autopct_with_revenue(pct, position["Total price"]), 
        startangle=90,
        pctdistance=0.9,
        wedgeprops=dict(width=width_chart_1, edgecolor='w'),
    )

    # List of pctdistance values for individual control

    change_label_radial_distance(pct_distances,autotexts,wedges)

    label_distance = 0.33
    pct_distance = 0.77
    width_chart_2 = 0.3
    
    wedges_2, texts_2, autotexts_2 = ax.pie(
        [
            position[position["Class"] == classe]["Total price"].sum() 
            for classe in unique_classes
        ],
        startangle=90,
        radius=1-width_chart_1, 
        colors=[plt.get_cmap(class_colors[classe])(0.55) for classe in unique_classes],
        wedgeprops=dict(width=width_chart_2, edgecolor='w'),
        autopct=lambda pct: autopct_with_revenue(pct, position["Total price"]),
        labels=unique_classes,
        pctdistance=pct_distance,
    )

    # Adjust the position of each percentage text
    change_label_radial_distance([label_distance],texts_2,wedges_2)

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Assets distribution')
    plt.show()

def plot_earnings_in_last_months(
        data_base:pd.DataFrame,
        delta_months:int,
    )->None:
    list_dates = [
        datetime(2024,datetime.today().month,1) - relativedelta(months=delta_months-i-1)
        for i in range(delta_months)]
    dict_positions = {
        date:compute_position(data_base,date=date)[0] for date in list_dates
    }

    dict_positions.update({datetime.today():compute_position(data_base)[0]})

    class_colors = {
        "total":"y",
        'USD':'r',
        'Tesouro':'g',
        'Ação': 'b',
        'FII': 'm',
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

    bar_width = 0.18
    x = np.arange(len(list_dates))

    # Create the plot
    fig, ax = plt.subplots()

    for i,_class in enumerate(class_colors.keys()):
        if _class == "total":
            total_per_month = [dict_positions[date]["Total price"].sum() for date in dict_positions.keys()]     
            earnings_per_month = [total_per_month[i+1] - total_per_month[i] for i in range(len(total_per_month)-1)]
        else:
            total_per_month = [dict_positions[date][dict_positions[date]["Class"] == _class]["Total price"].sum() for date in dict_positions.keys()] 
            earnings_per_month = [total_per_month[i+1] - total_per_month[i] for i in range(len(total_per_month)-1)]

        bars = ax.bar(
            x + i * bar_width,
            earnings_per_month, 
            color=[class_colors[_class] for x in earnings_per_month],
            width=bar_width,
            label=f"{_class}"
        )

    # Draw a central line at y=0
    ax.axhline(0, color='black', linewidth=0.8)

    # Add labels and title
    ax.set_xticks(x + bar_width * (len(class_colors) - 1) / 2)
    ax.set_xticklabels([month_names[month_num.month] for month_num in list_dates])
    ax.set_ylabel('Earnings/Losses (BRL)')
    ax.set_xlabel('Month')
    ax.set_title(f'Monthly changes in the last {delta_months} months')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Show the plot
    plt.show()