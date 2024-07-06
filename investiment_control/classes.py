from dataclasses import dataclass
from datetime import datetime
from asset_database import DICT_ASSET_INFO
from tools import get_value
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Portfolio:
    data_base:pd.DataFrame

    def __post_init__(self):
        self.data_base = self.process_data(self.data)
        self.data_base["class"] = [DICT_ASSET_INFO[ticker].asset_class for ticker in self.data_base["ticker"]]

    def compute_position(            
        self,
        date:datetime=datetime.today(),
        ) -> tuple[pd.DataFrame,pd.DataFrame]:
  
        _mask_actual_position = [0 != self.get_position(ticker,date)[1] for ticker in self.data_base["ticker"].unique()]
        _mask_old_assets = [0 == self.get_position(ticker,date)[1] for ticker in self.data_base["ticker"].unique()]

        _assets_in_actual_position = self.data_base["ticker"].unique()[_mask_actual_position]
        _assets_in_old_assets = self.data_base["ticker"].unique()[_mask_old_assets]

        _position = pd.DataFrame({
            "Ticker":[DICT_ASSET_INFO[ticker].name for ticker in _assets_in_actual_position],
            "Class":[DICT_ASSET_INFO[ticker].asset_class for ticker in _assets_in_actual_position],
            "Amount":[self.get_position(ticker,date)[1] for ticker in _assets_in_actual_position],
            "Cost per unit":[self.get_position(ticker,date)[0] for ticker in _assets_in_actual_position],
            "Price per unit":[get_value(ticker) for ticker in _assets_in_actual_position],
        })

        _old_assets = pd.DataFrame({
            "Ticker":[DICT_ASSET_INFO[ticker].name for ticker in _assets_in_old_assets],
            "Class":[DICT_ASSET_INFO[ticker].asset_class for ticker in _assets_in_old_assets],
            "Amount":[self.get_position(ticker,date)[1] for ticker in _assets_in_old_assets],
            "Cost per unit":[self.get_position(ticker,date)[0] for ticker in _assets_in_old_assets],
            "Price per unit":[get_value(ticker) for ticker in _assets_in_old_assets],
        })

        _position["Total cost"] = _position["Cost per unit"] * _position["Amount"]
        _position["Total price"] = _position["Price per unit"] * _position["Amount"]
        
        _position = _position.sort_values(by=["Class","Total price"],ascending=[True,False])
        _old_assets = _old_assets.sort_values("Class")

        return _position,_old_assets

    def get_position(
            self,
            ticker:str,
            date:datetime=datetime.today(),
        )->tuple[float,float,float]:

        operation = self.data_base[(self.data_base["ticker"] == ticker) & (self.data_base["date"] <= date)]

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

    # def get_values(self,dict_values_to_filter) -> pd.DataFrame:

    #     mask = self.data["buy"]==self.data["buy"]
    #     for column,value in dict_values_to_filter.items():
    #         mask = (self.data[column]==value) & mask
    #     return self.data[mask]

    def plot_actual_postion(self):
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

        unique_classes = self.actual_position["Class"].unique()
        class_store_counts = {cls: (self.actual_position["Class"] == cls).sum() for cls in unique_classes}
        class_colors_tones = {cls: generate_colors(class_colors[cls], count) for cls, count in class_store_counts.items()}

        store_colors = []
        class_color_index = {cls: 0 for cls in unique_classes}

        for cls in self.actual_position["Class"]:
            store_colors.append(class_colors_tones[cls][class_color_index[cls]])
            class_color_index[cls] += 1

        pct_distances = [0.9,0.70]
        width_chart_1 = 0.4

        fig, ax = plt.subplots(figsize=(12,8))
        wedges, texts, autotexts = ax.pie(
            self.actual_position["Price per unit"]*self.actual_position["Amount"], 
            labels=self.actual_position["Ticker"], 
            colors=store_colors, 
            autopct=lambda pct: autopct_with_revenue(pct, self.actual_position["Total price"]), 
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
                self.actual_position[self.actual_position["Class"] == classe]["Total price"].sum() 
                for classe in unique_classes
            ],
            startangle=90,
            radius=1-width_chart_1, 
            colors=[plt.get_cmap(class_colors[classe])(0.55) for classe in unique_classes],
            wedgeprops=dict(width=width_chart_2, edgecolor='w'),
            autopct=lambda pct: autopct_with_revenue(pct, self.actual_position["Total price"]),
            labels=unique_classes,
            pctdistance=pct_distance,
        )

        # Adjust the position of each percentage text
        change_label_radial_distance([label_distance],texts_2,wedges_2)

        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Assets distribution')
        plt.show()

##### unused #####
@dataclass
class Transaction:
    owner:str
    date:datetime
    ticker:str
    buy:bool
    price:float
    amount:int
    curency:str="BRL"

@dataclass
class Position:
    owner:str
    date:datetime
    ticker:str
    buy:bool
    price:float
    amount:int
    curency:str="BRL"







