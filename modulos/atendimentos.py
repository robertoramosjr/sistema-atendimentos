import streamlit as st
from datetime import date
from services import listar_clientes, registrar_atendimento, listar_atendimentos, atualizar_atendimento

# Categorias pré-definidas
CATEGORIAS = ["Ansiedade", "Autoestima", "Relacionamentos", "Família", "Foco", "Humor", "Estudos", "Trabalho"]

def render(cursor, conn):
    st.header("📅 Registrar atendimento")

    # Listar clientes ativos
    clientes = listar_clientes(cursor)
    if not clientes:
        st.warning("Cadastre ao menos um cliente antes de registrar atendimentos.")
        return

    nomes = [nome for _, nome in clientes]
    id_map = {nome: id_ for id_, nome in clientes}

    cliente_nome = st.selectbox("Cliente", nomes)
    data_atendimento = st.date_input("Data do atendimento", value=date.today())
    prontuario = st.text_area("Anotações do prontuário (opcional)", height=150)
    categorias = st.multiselect("Categorias (opcional):", CATEGORIAS)

    if st.button("Registrar atendimento"):
        cliente_id = id_map[cliente_nome]
        categorias_str = ", ".join(categorias)
        registrar_atendimento(cursor, conn, cliente_id, str(data_atendimento), prontuario.strip(), categorias_str)
        st.success(f"Atendimento de {cliente_nome} em {data_atendimento.strftime('%d/%m/%Y')} registrado.")

    # Histórico de atendimentos
    st.subheader("📋 Histórico de atendimentos")
    atendimentos = listar_atendimentos(cursor)

    if atendimentos:
        for i, (nome, data_str, anotacao, categorias) in enumerate(atendimentos):
            with st.expander(f"{nome} — {data_str}", expanded=False):
                st.markdown("📝 **Prontuário:**")
                st.markdown(f"_{anotacao or 'Sem anotações.'}_")

                if categorias:
                    st.markdown(f"🏷️ **Categorias:** `{categorias}`")

                novo_prontuario = st.text_area("Editar prontuário:", value=anotacao or "", key=f"edit_{i}")
                novas_categorias = st.text_input("Editar categorias (separadas por vírgula):", value=categorias or "", key=f"cat_{i}")

                if st.button("💾 Salvar alterações", key=f"salvar_{i}"):
                    atualizar_atendimento(cursor, conn, nome, data_str, novo_prontuario.strip(), novas_categorias.strip())
                    st.success("Atendimento atualizado com sucesso! Atualize a página para ver a alteração.")
    else:
        st.info("Nenhum atendimento registrado ainda.")
