import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services import registrar_pagamento

def render(cursor, conn):
    st.subheader("📅 Histórico de Pagamentos por Cliente")

    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    nomes_clientes = [nome for _, nome in clientes]
    cliente_selecionado = st.selectbox("Selecione um cliente", nomes_clientes)

    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: date(1900, m, 1).strftime('%B'))
    with col2:
        ano = st.number_input("Ano", min_value=2000, max_value=date.today().year, value=date.today().year)

    cliente_id = [cid for cid, nome in clientes if nome == cliente_selecionado][0]

    inicio = date(ano, mes, 1)
    fim = date(ano, mes, 28) + timedelta(days=4)
    fim = fim - timedelta(days=fim.day)
    cursor.execute("""
        SELECT data, valor, descricao FROM pagamentos
        WHERE cliente_id = ? AND data BETWEEN ? AND ?
        ORDER BY data
    """, (cliente_id, inicio.isoformat(), fim.isoformat()))
    pagamentos = cursor.fetchall()

    if pagamentos:
        df_pagamentos = pd.DataFrame(pagamentos, columns=["Data", "Valor", "Descrição"])
        df_pagamentos["Data"] = pd.to_datetime(df_pagamentos["Data"]).dt.strftime("%d/%m/%Y")
        st.dataframe(df_pagamentos, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pagamento registrado neste período.")

    total_pago = sum(p[1] for p in pagamentos)

    cursor.execute("SELECT valor_consulta, frequencia, frequencia_pagamento FROM clientes WHERE id = ?", (cliente_id,))
    valor_consulta, freq_atend, freq_pag = cursor.fetchone()

    if freq_pag == "Mensal":
        esperado = valor_consulta * (4 if freq_atend == "Semanal" else 2 if freq_atend == "Quinzenal" else 1)
    elif freq_pag == "Por sessão":
        cursor.execute("""
            SELECT COUNT(*) FROM atendimentos
            WHERE cliente_id = ? AND data BETWEEN ? AND ?
        """, (cliente_id, inicio.isoformat(), fim.isoformat()))
        num_sessoes = cursor.fetchone()[0]
        esperado = valor_consulta * num_sessoes
    else:
        esperado = 0

    st.markdown("---")
    col1, col2 = st.columns(2)
    col1.metric("💸 Total pago", f"R$ {total_pago:.2f}")
    col2.metric("📊 Valor esperado", f"R$ {esperado:.2f}")

    if total_pago >= esperado:
        st.success("✅ Pagamento em dia!")
    else:
        st.warning(f"⚠️ Valor em aberto: R$ {esperado - total_pago:.2f}")

    st.markdown("---")
    st.subheader("💳 Registrar novo pagamento")
    with st.form("form_pagamento"):
        data_pagamento = st.date_input("Data do pagamento", value=date.today())
        valor_pagamento = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        descricao_pagamento = st.text_input("Descrição (opcional)")
        confirmar = st.form_submit_button("Registrar")

        if confirmar:
            if valor_pagamento > 0:
                registrar_pagamento(cursor, conn, cliente_id, data_pagamento.isoformat(), valor_pagamento, descricao_pagamento)
                st.success("Pagamento registrado com sucesso!")
                st.rerun()
            else:
                st.warning("O valor deve ser maior que zero.")
