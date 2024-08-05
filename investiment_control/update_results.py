import pandas as pd
from classes import Portfolio
from transactions import GLOBAL_DATA_BASE
from dateutil.relativedelta import relativedelta
from tools import plot_position_table,plot_position_graph,plot_earnings_in_last_months,plot_dividends_in_last_months

portfolio_luiz = Portfolio(GLOBAL_DATA_BASE[GLOBAL_DATA_BASE["owner"]=="Luiz"].drop("owner",axis=1),"Luiz")
portfolio_luciane = Portfolio(GLOBAL_DATA_BASE[GLOBAL_DATA_BASE["owner"]=="Luciane"].drop("owner",axis=1),"Luciane")

###### ploting ploting earnings and dividends in last months #####
plot_earnings_in_last_months(portfolio_luiz,delta_months=12,save_image=True,plot_image=False)
plot_dividends_in_last_months(portfolio_luiz,delta_months=12,save_image=True,plot_image=False)
plot_earnings_in_last_months(portfolio_luciane,delta_months=12,save_image=True,plot_image=False)
plot_dividends_in_last_months(portfolio_luciane,delta_months=12,save_image=True,plot_image=False)

###### ploting positions in last months #####
delta_months = 2

list_dates = [
    pd.Timestamp(2024,pd.Timestamp.today().month,1) - relativedelta(months=delta_months-i-1)
    for i in range(delta_months)]

for date in list_dates: 
    plot_position_table(portfolio_luiz,date,save_image=True,plot_image=False)
    plot_position_table(portfolio_luciane,date,save_image=True,plot_image=False)
