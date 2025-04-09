# Estrutura principal com carregamento modular
import streamlit as st
from db import conectar, setup_financeiro
import modulos.cadastro as cadastro
import modulos.atendimentos as atendimentos
import modulos.fluxo_caixa as fluxo
import modulos.pagamentos as pagamentos
import modulos.recibos as recibos
import modulos.visao_geral as visao
import modulos.configuracoes as configuracoes
import modulos.evolucao as evolucao
import modulos.services
from services import checar_autenticacao

checar_autenticacao()

# Conexão com banco de dados
conn, cursor = conectar()
setup_financeiro(cursor, conn)

# Configurações gerais
st.set_page_config(page_title="Sistema da Psicóloga", page_icon="🧠")
st.title("Sistema de Atendimentos 🧠")

# Menu lateral
menu = st.sidebar.radio("Menu", [
    "📋 Cadastro de Clientes",
    "📅 Registrar Atendimentos",
    "📈 Evolução por Cliente",
    "💳 Pagamentos",
    "📊 Visão Geral de Pagamentos",
    "📄 Recibos",
    "💵 Fluxo de Caixa",
    "⚙️ Configurações"
])

# Importar e renderizar cada módulo conforme a aba
if menu == "📋 Cadastro de Clientes":
        cadastro.render(cursor, conn)

elif menu == "📅 Registrar Atendimentos":
      atendimentos.render(cursor, conn)

elif menu == "📈 Evolução por Cliente":
       evolucao.render(cursor, conn)

elif menu == "💳 Pagamentos":
       pagamentos.render(cursor, conn)

elif menu == "📄 Recibos":
      recibos.render(cursor, conn)

elif menu == "💵 Fluxo de Caixa":
    fluxo.render(cursor, conn)

elif menu == "📊 Visão Geral de Pagamentos":
    visao.render(cursor, conn)

elif menu == "⚙️ Configurações":
    configuracoes.render(cursor, conn)
