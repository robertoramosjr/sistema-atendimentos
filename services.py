from num2words import num2words
from datetime import datetime


def adicionar_cliente(cursor, conn, nome, cpf, valor, frequencia, freq_pagamento, ativo):
    cursor.execute("""
        INSERT INTO clientes (nome, cpf, valor_consulta, frequencia, frequencia_pagamento, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, cpf, valor, frequencia, freq_pagamento, int(ativo)))
    conn.commit()

def listar_clientes(cursor):
    cursor.execute("SELECT id, nome FROM clientes WHERE ativo = 1")
    return cursor.fetchall()

def obter_valor_por_cliente(cursor, cliente_id):
    cursor.execute("SELECT valor_consulta FROM clientes WHERE id = ?", (cliente_id,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def registrar_atendimento(cursor, conn, cliente_id, data_str, prontuario, categorias):
    cursor.execute("""
        INSERT INTO atendimentos (cliente_id, data, prontuario, categorias)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, data_str, prontuario, categorias))
    conn.commit()

def listar_atendimentos(cursor):
    cursor.execute("""
        SELECT c.nome, a.data, a.prontuario, a.categorias
        FROM atendimentos a
        JOIN clientes c ON a.cliente_id = c.id
        ORDER BY a.data DESC
    """)
    return cursor.fetchall()

def atualizar_atendimento(cursor, conn, nome_cliente, data_str, prontuario, categorias):
    cursor.execute("""
        UPDATE atendimentos
        SET prontuario = ?, categorias = ?
        WHERE rowid = (
            SELECT a.rowid
            FROM atendimentos a
            JOIN clientes c ON a.cliente_id = c.id
            WHERE c.nome = ? AND a.data = ?
            LIMIT 1
        )
    """, (prontuario, categorias, nome_cliente, data_str))
    conn.commit()

def alterar_status_cliente(cursor, conn, cliente_id, ativo):
    cursor.execute("UPDATE clientes SET ativo = ? WHERE id = ?", (ativo, cliente_id))
    conn.commit()

def registrar_pagamento(cursor, conn, cliente_id, data, valor, descricao):
    cursor.execute("INSERT INTO pagamentos (cliente_id, data, valor, descricao) VALUES (?, ?, ?, ?)",
                   (cliente_id, data, valor, descricao))
    descricao_caixa = f"Pagamento de cliente {cliente_id}" + (f" - {descricao}" if descricao else "")
    cursor.execute("INSERT INTO caixa (data, tipo, descricao, valor) VALUES (?, 'entrada', ?, ?)",
                   (data, descricao_caixa, valor))
    conn.commit()

def registrar_movimentacao_caixa(cursor, conn, data, tipo, descricao, valor):
    cursor.execute("INSERT INTO caixa (data, tipo, descricao, valor) VALUES (?, ?, ?, ?)",
                   (data, tipo, descricao, valor))
    conn.commit()

def calcular_saldo_atual(cursor):
    # Pega o valor inicial do caixa
    cursor.execute("SELECT valor FROM valor_inicial WHERE id = 1")
    valor_inicial = cursor.fetchone()[0]

    # Soma entradas e saídas
    cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'entrada'")
    entradas = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'saida'")
    saidas = cursor.fetchone()[0] or 0.0

    saldo = valor_inicial + entradas - saidas
    return saldo

def calcular_total_pagamentos_cliente(cursor, cliente_id, data_inicio, data_fim):
    cursor.execute("""
        SELECT SUM(valor) FROM pagamentos
        WHERE cliente_id = ? AND data BETWEEN ? AND ?
    """, (cliente_id, data_inicio, data_fim))
    return cursor.fetchone()[0] or 0

def contar_sessoes_no_periodo(cursor, cliente_id, data_inicio, data_fim):
    cursor.execute("""
        SELECT COUNT(*) FROM atendimentos
        WHERE cliente_id = ? AND data BETWEEN ? AND ?
    """, (cliente_id, data_inicio, data_fim))
    return cursor.fetchone()[0] or 0

def resetar_banco_de_dados(cursor, conn):
    cursor.execute("DELETE FROM atendimentos")
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM pagamentos")
    cursor.execute("DELETE FROM caixa")
    cursor.execute("UPDATE valor_inicial SET valor = 0 WHERE id = 1")
    conn.commit()
    
def valor_por_extenso(valor):
    try:
        return num2words(valor, lang='pt_BR').replace(" e", ",")
    except:
        return "valor inválido"

def formatar_data_br(data_iso):
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_iso

def ultimo_dia_do_mes(ano, mes):
    from datetime import date, timedelta
    fim = date(ano, mes, 28) + timedelta(days=4)
    return fim - timedelta(days=fim.day)
