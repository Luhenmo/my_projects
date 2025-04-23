import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os
from pathlib import Path
from utils.tools import compute_position,plot_position_graph


current_path = Path(__file__).parent.resolve()

#### Setting page ####
st.set_page_config(
    page_title="📊 Controle de investimentos",
    page_icon="📊",
    layout="centered"
)
st.title("📊 Controle de investimentos")


#### Load data ####
ARQUIVO_DADOS = current_path/"data"/"historico_transacoes.csv"


#### Import data ####
base_dados = pd.read_csv(ARQUIVO_DADOS)
base_dados["Data"] = pd.to_datetime(base_dados["Data"], format="%Y-%m-%d")


# ---- Interface para seleção de data e moeda ----
st.sidebar.header("Configurações")

# Seleção de data com padrão para hoje
data_selecionada = st.sidebar.date_input(
    "Selecione a data:",
    value=pd.Timestamp.today()
)
data_selecionada = pd.to_datetime(data_selecionada)
# Seleção de moeda
moeda_selecionada = st.sidebar.selectbox(
    "Selecione a moeda:",
    options=["EUR", "USD", "BRL"],
    index=2  # Define BRL como padrão
)

# ---- Lista de donos disponíveis ----
lista_donos = sorted(base_dados["Dono"].unique())

# ---- Interface para seleção de donos ----
donos_selecionados = st.multiselect(
    "👤 Selecione o(s) dono(s) para visualizar posição atual:",
    options=lista_donos,
    default=[],
)

# ---- Exibir apenas os selecionados ----
if donos_selecionados:
    for name in donos_selecionados:

        dados = base_dados[base_dados["Dono"] == name]

        st.markdown(f"### 📌 Posição de **{name}** ({data_selecionada.strftime("%Y-%m-%d")})")
        position = compute_position(dados, data_selecionada, moeda_selecionada)
        # Adicionar coluna "Lucro (%)"
        position["Lucro (%)"] = ((position["Valor total"] - position["Custo total"]) / position["Custo total"]) * 100

        # Aplicar formatação condicional
        def highlight_profit(val):
            """
            Aplica cores com base no valor do lucro:
            - Verde para lucro (> 0)
            - Amarelo para valores próximos de 0 (-5% a 5%)
            - Vermelho para prejuízo (< 0)
            """
            if val > 5:
                color = 'background-color: #d4edda; color: #155724;'  # Verde
            elif -5 <= val <= 5:
                color = 'background-color: #fff3cd; color: #856404;'  # Amarelo
            else:
                color = 'background-color: #f8d7da; color: #721c24;'  # Vermelho
            return color
            
        def generate_formated_possition(position):
            styled_position = position.style.applymap(
                highlight_profit, subset=["Lucro (%)"]
            ).format({
                "Custo unitário": "R${:,.2f}",
                "Preço unitário": "R${:,.2f}",
                "Custo total": "R${:,.2f}",
                "Valor total": "R${:,.2f}",
                "Lucro (%)": "{:+.2f}%",
            })
            return styled_position

        # Exibir gráfico e DataFrame estilizado
        st.pyplot(plot_position_graph(position, plot_image=False))
        st.dataframe(generate_formated_possition(position), use_container_width=True)
else:
    st.info("Selecione pelo menos um dono para exibir os dados.")

