
import streamlit as st
import pandas as pd
from datetime import date
from utils.asset_database import DICT_ASSET_INFO
import os
from pathlib import Path

current_path = Path(__file__).parent.resolve()

# ---------- CONFIGURAÇÕES ----------
ARQUIVO_DADOS = current_path.parent/"data"/"historico_transacoes.csv"

ATIVOS_DISPONIVEIS = [asset.name for asset in DICT_ASSET_INFO.values()]

# ---------- INICIALIZAÇÃO ----------
if "transacoes_temp" not in st.session_state:
    st.session_state.transacoes_temp = pd.DataFrame(columns=["Dono","Data","Ativo","C/V","Preço","Qnt","Moeda"])

# ---------- FUNÇÕES AUXILIARES ----------
def carregar_dados_csv():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=["Dono","Data","Ativo","C/V","Preço","Qnt","Moeda"])

def salvar_no_csv():
    df_existente = carregar_dados_csv()
    if df_existente.empty:
        df_novo = st.session_state.transacoes_temp
    else:
        df_novo = pd.concat([st.session_state.transacoes_temp,df_existente], ignore_index=True)
    df_novo.to_csv(ARQUIVO_DADOS, index=False)
    st.session_state.transacoes_temp = pd.DataFrame(columns=["Dono","Data","Ativo","C/V","Preço","Qnt","Moeda"])  # limpa após salvar

# ---------- APP STREAMLIT ----------
st.set_page_config(
    page_title="📝 Controle de transações",
    page_icon="📝",
    layout="centered"
)
st.title("📝 Controle de transações")

# Formulário
with st.form("form_transacao"):
    col1_11, col_12, col_13 = st.columns(3)
    with col1_11:
        ativo = st.selectbox("Ativo", sorted(ATIVOS_DISPONIVEIS))
    with col_12:
        dono = st.radio("Proprietário", ["Luiz", "Luciane"], horizontal=True)
    with col_13:
        moeda = st.radio("Moeda", ["BRL", "USD", "EUR"], horizontal=True)

    col_21, col_22, col_23 = st.columns(3)
    with col_21:
        preco = st.number_input("Preço unitário", min_value=0.0, step=0.01)
    with col_22:
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
    with col_23:
        data_transacao = st.date_input("Data", value=date.today())

    col_31, col_32 = st.columns(2)
    with col_31:
        submitted = st.form_submit_button("➕ Adicionar à lista")
    with col_32:
        tipo = st.radio("Tipo", ["Compra", "Venda"], horizontal=True)
        dict_tipo = {"Compra":"C","Venda":"V"}
        tipo = dict_tipo[tipo]

# Ao adicionar
if submitted:
    nova = pd.DataFrame([{
        "Dono": dono,
        "Data": data_transacao,
        "Ativo": ativo,
        "C/V": tipo,
        "Preço": preco,
        "Qnt": quantidade,
        "Moeda": moeda,
    }])
    if st.session_state.transacoes_temp.empty:
        st.session_state.transacoes_temp = nova
    else:
        st.session_state.transacoes_temp = pd.concat([st.session_state.transacoes_temp, nova], ignore_index=True)
    # st.success("Transação adicionada à lista temporária.")

# Mostrar transações temporárias
st.subheader("📝 Transações pendentes (não salvas)")

if st.session_state.transacoes_temp.empty:
    st.info("Nenhuma transação pendente.")
else:
    if st.button("↩️ Undo"):
        st.session_state.transacoes_temp.drop(st.session_state.transacoes_temp.index[-1], inplace=True)
        st.rerun()

    st.dataframe(st.session_state.transacoes_temp.sort_values(by="Data", ascending=False), use_container_width=True)

    col_11, col_12, = st.columns(2)
    # Botão para salvar tudo
    if st.button("💾 Salvar todas no arquivo CSV"):
        salvar_no_csv()
        st.rerun()




# Mostrar histórico do CSV
st.subheader("📊 Histórico salvo no CSV")
df_historico = carregar_dados_csv()

# ---------- HISTÓRICO DO CSV COM OPÇÃO DE EXCLUSÃO ---------- #
if df_historico.empty:
    st.info("Nenhum dado salvo no arquivo ainda.")
else:
    st.dataframe(df_historico.sort_values(by="Data", ascending=False), use_container_width=True)

