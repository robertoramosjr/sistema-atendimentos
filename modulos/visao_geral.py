import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services import calcular_total_pagamentos_cliente, contar_sessoes_no_periodo

def render(cursor, conn):
    st.header("📊 Visão Geral de Pagamentos")

    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: date(1900, m, 1).strftime('%B'))
    with col2:
        ano = st.selectbox("Ano", list(range(2020, date.today().year + 1))[::-1], index=0)

    data_inicio = date(ano, mes, 1)
    data_fim = date(ano, mes, 28) + timedelta(days=4)
    data_fim = data_fim - timedelta(days=data_fim.day)

    cursor.execute("SELECT id, nome, valor_consulta, frequencia, frequencia_pagamento FROM clientes WHERE ativo = 1")
    clientes = cursor.fetchall()

    linhas = []
    for cid, nome, valor, freq_atend, freq_pag in clientes:
        total_pago = calcular_total_pagamentos_cliente(cursor, cid, data_inicio.isoformat(), data_fim.isoformat())

        if freq_pag == "Mensal":
            esperado = valor * (4 if freq_atend == "Semanal" else 2 if freq_atend == "Quinzenal" else 1)
        elif freq_pag == "Por sessão":
            sessoes = contar_sessoes_no_periodo(cursor, cid, data_inicio.isoformat(), data_fim.isoformat())
            esperado = valor * sessoes
        else:
            esperado = 0

        status = "✅ Em dia" if total_pago >= esperado else f"❌ Em aberto (R$ {esperado - total_pago:.2f})"
        linhas.append((nome, f"R$ {total_pago:.2f}", f"R$ {esperado:.2f}", status))

    if linhas:
        df = pd.DataFrame(linhas, columns=["Cliente", "Pago", "Esperado", "Situação"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        pagos = sum(float(l[1].replace("R$", "").replace(",", ".")) for l in linhas)
        esperados = sum(float(l[2].replace("R$", "").replace(",", ".")) for l in linhas)

        col1, col2 = st.columns(2)
        col1.metric("💸 Total pago no período", f"R$ {pagos:.2f}")
        col2.metric("📊 Total esperado", f"R$ {esperados:.2f}")
    else:
        st.info("Nenhum cliente ativo encontrado para exibir.")