import streamlit as st
from services import adicionar_cliente, listar_clientes, alterar_status_cliente


def render(cursor, conn):
    st.header("Cadastrar novo cliente")
    with st.form("form_cliente"):
        nome = st.text_input("Nome do cliente")
        cpf = st.text_input("CPF do cliente (opcional)")
        valor = st.number_input("Valor por consulta (R$)", min_value=0.0, step=10.0, format="%.2f")
        frequencias_possiveis = ["Semanal", "Quinzenal"]
        frequencia = st.selectbox("Frequência esperada de atendimento:", frequencias_possiveis)
        frequencia_pagamento = st.selectbox("Frequência de pagamento:", ["Mensal", "Por sessão"])
        ativo = st.checkbox("Cliente ativo?", value=True)
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if nome.strip() == "":
                st.warning("Digite o nome do cliente.")
            else:
                adicionar_cliente(cursor, conn, nome.strip(), cpf.strip(), valor, frequencia, frequencia_pagamento, ativo)
                st.success(f"Cliente '{nome}' cadastrado com valor de R$ {valor:.2f}.")

    st.subheader("👥 Clientes já cadastrados")
    cursor.execute("SELECT nome, valor_consulta, frequencia, frequencia_pagamento FROM clientes WHERE ativo = 1 ORDER BY nome")
    clientes = cursor.fetchall()

    for nome, valor, frequencia, freq_pag in clientes:
        st.write(f"🧑 {nome} | 💰 R$ {valor:.2f} | ⏱️ Atendimentos: {frequencia} | 💳 Pagamentos: {freq_pag}")

    st.subheader("👥 Gerenciar clientes")
    filtro = st.text_input("🔍 Buscar cliente por nome:")

    st.subheader("Clientes ativos")
    cursor.execute("SELECT id, nome FROM clientes WHERE ativo = 1 ORDER BY nome")
    clientes_ativos = cursor.fetchall()
    clientes_filtrados_ativos = [c for c in clientes_ativos if filtro.lower() in c[1].lower()]

    if clientes_filtrados_ativos:
        for cid, nome in clientes_filtrados_ativos:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{nome}** - 🟢 Ativo")
            with col2:
                if st.button("Desativar", key=f"desativar_{cid}"):
                    alterar_status_cliente(cursor, conn, cid, 0)
                    st.rerun()
    else:
        st.info("Nenhum cliente ativo encontrado com esse nome.")

    st.markdown("---")
    st.subheader("Clientes inativos")
    cursor.execute("SELECT id, nome FROM clientes WHERE ativo = 0 ORDER BY nome")
    clientes_inativos = cursor.fetchall()
    clientes_filtrados_inativos = [c for c in clientes_inativos if filtro.lower() in c[1].lower()]

    if clientes_filtrados_inativos:
        for cid, nome in clientes_filtrados_inativos:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{nome}** - 🔴 Inativo")
            with col2:
                if st.button("Ativar", key=f"ativar_{cid}"):
                    alterar_status_cliente(cursor, conn, cid, 1)
                    st.rerun()
    else:
        st.info("Nenhum cliente inativo encontrado com esse nome.")