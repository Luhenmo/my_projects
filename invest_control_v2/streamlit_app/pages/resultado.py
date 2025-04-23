import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from utils.tools import compute_dividends,get_field_for_assets_in_position,compute_position


current_path = Path(__file__).parent.parent.resolve()

#### Setting page ####
st.set_page_config(
    page_title="📅 Histórico",
    page_icon="📅",
    layout="centered"
)
st.title("📅 Resultado mensal")

#### Load data ####
ARQUIVO_DADOS = current_path / "data" / "historico_transacoes.csv"

#### Import data ####
base_dados = pd.read_csv(ARQUIVO_DADOS)
base_dados["Data"] = pd.to_datetime(base_dados["Data"], format="%Y-%m-%d")

lista_donos = sorted(base_dados["Dono"].unique())
# ---- Interface para seleção de donos ----
donos_selecionados = st.multiselect(
    "👤 Selecione o(s) dono(s) para visualizar posição atual:",
    options=lista_donos,
    default=[],
)


dict_dividendos_dono = {}
### Calculando dividendo global por dono
for name in donos_selecionados:
    dividendos = compute_dividends(base_dados[base_dados["Dono"] == name])
    dict_dividendos_dono.update({name:dividendos})

# ---- Interface para seleção de ano e mês ----
st.sidebar.header("Data")
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", base_dados["Data"].dt.year.unique())
mes_selecionado = st.sidebar.selectbox("Selecione o mês:", range(1, 13), format_func=lambda x: f"{x:02d}")

for name in donos_selecionados:
    # Filtrar os dados com base no ano e mês selecionados
    dividendos = dict_dividendos_dono[name]
    dividendos_mensais = dividendos[
        (dividendos["Data"].apply(lambda value: value.year) == ano_selecionado) &
        (dividendos["Data"].apply(lambda value: value.month) == mes_selecionado)
    ].drop(["Data"],axis=1)

    dividendos_mensais.sort_values(by="Classe",ignore_index=True)

    dividendos_agrupados = pd.DataFrame(
        columns=dividendos_mensais["Classe"].unique(),
        data=[[
            dividendos_mensais[dividendos_mensais["Classe"] == classe]["Dividendo total"].sum()
            for classe in dividendos_mensais["Classe"].unique()
        ]]
    )

    dividendos_agrupados["Total"] = dividendos_agrupados.apply(sum,axis=1)

    # ---- DataFrame de dividendos pagos ----
    st.subheader(f"📈 Dividendos pagos em {mes_selecionado:02d}/{ano_selecionado} (**{name}**)")
    if not dividendos_mensais.empty:

        # Exibir os dividendos agrupados em formato Markdown
        classes = " | ".join(dividendos_agrupados.columns)  # Excluir a coluna "Total"
        valores = " | ".join([f"R${valor:,.2f}" for valor in dividendos_agrupados.iloc[0].values])  # Excluir o total
        total = f"**Total:** R${dividendos_agrupados['Total'].iloc[0]:,.2f}"

        st.markdown(f"""
        | {classes} |
        | {'--- | ' * len(dividendos_agrupados.columns)}|
        | {valores} |
        """, unsafe_allow_html=True)

        st.dataframe(dividendos_mensais, use_container_width=True)
    else:
        st.info("Nenhum dividendo pago neste mês.")

    # ---- DataFrame de movimentações financeiras ----
    st.subheader(f"💰 Movimentações financeiras em {mes_selecionado:02d}/{ano_selecionado}")

    position = compute_position(base_dados[base_dados["Dono"] == "Luiz"],pd.Timestamp(year=ano_selecionado,month=mes_selecionado,day=1))

    movimentacao = base_dados[
        (base_dados["Data"].apply(lambda value: value.year) == ano_selecionado) &
        (base_dados["Data"].apply(lambda value: value.month) == mes_selecionado) &
        (base_dados["Dono"] == name)
    ].drop(["Dono"],axis=1)

    compras = movimentacao[movimentacao["C/V"] == "C"]
    vendas = movimentacao[movimentacao["C/V"] == "V"]

    resultado_compra = pd.DataFrame({
        "Ativo":compras["Ativo"],
        "Preço médio":get_field_for_assets_in_position(position,compras["Ativo"],"Preço unitário"),
        "Qnt atual":get_field_for_assets_in_position(position,compras["Ativo"],"Qnt"),
        "Valor atual":get_field_for_assets_in_position(position,compras["Ativo"],"Preço unitário") * get_field_for_assets_in_position(position,compras["Ativo"],"Qnt"),
        "Preço compra":compras["Preço"],
        "Qtn compra":compras["Qnt"],
        "Valor comprado":compras["Preço"]*compras["Qnt"],
    })

    resultado_venda = pd.DataFrame({
        "Ativo":vendas["Ativo"],
        "Preço médio":get_field_for_assets_in_position(position,vendas["Ativo"],"Preço unitário"),
        "Qnt atual":get_field_for_assets_in_position(position,vendas["Ativo"],"Qnt"),
        "Valor atual":get_field_for_assets_in_position(position,vendas["Ativo"],"Preço unitário") * get_field_for_assets_in_position(position,vendas["Ativo"],"Qnt"),
        "Preço venda":vendas["Preço"],
        "Qtn venda":vendas["Qnt"],
        "Valor vendido":vendas["Preço"]*vendas["Qnt"],
    })

    resultado_venda["Lucro"] = resultado_venda.apply(lambda row: (row["Preço venda"]-row["Preço médio"]) * row["Qtn venda"],axis=1)
    

    st.subheader(f"Compras")
    if not resultado_compra.empty:

        st.dataframe(resultado_compra, use_container_width=True)

    else:
        st.info("Nenhuma compra neste mês.")

    st.subheader(f"Vendas")
    if not resultado_venda.empty:

        st.dataframe(resultado_venda, use_container_width=True)
    else:
        st.info("Nenhuma compra neste mês.")

    