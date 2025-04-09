import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import io
from services import registrar_movimentacao_caixa, calcular_saldo_atual

def render(cursor, conn):
    st.header("💰 Fluxo de Caixa")

    # Valor inicial do caixa
    cursor.execute("SELECT valor FROM valor_inicial WHERE id = 1")
    valor_inicial = cursor.fetchone()[0]
    novo_valor = st.number_input("💵 Valor inicial do caixa", value=valor_inicial, step=10.0, format="%.2f")
    if novo_valor != valor_inicial:
        cursor.execute("UPDATE valor_inicial SET valor = ? WHERE id = 1", (novo_valor,))
        conn.commit()
        st.success("Valor inicial atualizado!")

    st.markdown("---")

    # Formulário de movimentação
    with st.form("form_movimentacao"):
        tipo = st.selectbox("Tipo de movimentação", ["entrada", "saida"])
        data_mov = st.date_input("Data", value=date.today())
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Registrar")

        if submitted:
            if valor > 0:
                registrar_movimentacao_caixa(cursor, conn, data_mov.isoformat(), tipo, descricao, valor)
                st.success("Movimentação registrada com sucesso!")
                st.rerun()
            else:
                st.warning("Informe um valor maior que zero.")

    st.markdown("---")
    st.subheader("📆 Filtrar movimentações por período")

    col1, col2 = st.columns(2)
    with col1:
        ano = st.selectbox("Ano", list(range(2020, date.today().year + 1))[::-1])
    with col2:
        mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: date(1900, m, 1).strftime("%B"))

    data_inicio = date(ano, mes, 1)
    data_fim = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)

    cursor.execute("""
        SELECT data, tipo, descricao, valor FROM caixa
        WHERE data >= ? AND data < ?
        ORDER BY data DESC
    """, (data_inicio.isoformat(), data_fim.isoformat()))
    historico = cursor.fetchall()

    if historico:
        df = pd.DataFrame(historico, columns=["Data", "Tipo", "Descrição", "Valor"])
        df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y")
        st.dataframe(df, hide_index=True, use_container_width=True)

        total_entradas = sum(row[3] for row in historico if row[1] == "entrada")
        total_saidas = sum(row[3] for row in historico if row[1] == "saida")

        col1, col2 = st.columns(2)
        col1.metric("📥 Total de entradas", f"R$ {total_entradas:,.2f}".replace(".", ","))
        col2.metric("📤 Total de saídas", f"R$ {total_saidas:,.2f}".replace(".", ","))

        # Gráfico de pizza
        st.markdown("### 📊 Distribuição das movimentações")
        fig, ax = plt.subplots()
        ax.pie([total_entradas, total_saidas], labels=["Entradas", "Saídas"], autopct="%.1f%%", startangle=90,
               colors=["#2ecc71", "#e74c3c"])
        ax.axis("equal")
        st.pyplot(fig)

        # Exportar para Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Fluxo de Caixa")
        output.seek(0)

        st.download_button(
            label="📥 Exportar para Excel",
            data=output,
            file_name=f"fluxo_caixa_{ano}_{mes:02d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("Nenhuma movimentação encontrada nesse período.")

    st.markdown("---")
    saldo = calcular_saldo_atual(cursor)
    st.metric("💼 Saldo atual do caixa", f"R$ {saldo:.2f}")
