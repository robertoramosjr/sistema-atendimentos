import streamlit as st
from services import resetar_banco_de_dados

def render(cursor, conn):
    st.header("⚙️ Configurações do Sistema")

    st.warning("⚠️ Essa ação é irreversível!")

    if st.button("🧨 Zerar banco de dados"):
        resetar_banco_de_dados(cursor, conn)
        st.success("Banco de dados zerado com sucesso!")