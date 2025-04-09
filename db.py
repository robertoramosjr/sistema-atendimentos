import sqlite3

def conectar():
    conn = sqlite3.connect("banco_psicologa.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor

def setup_financeiro(cursor, conn):
    # Tabela de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT,
            valor_consulta REAL NOT NULL,
            frequencia TEXT DEFAULT 'Semanal',
            frequencia_pagamento TEXT DEFAULT 'Mensal',
            ativo INTEGER DEFAULT 1
        )
    """)

    # Tabela de atendimentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            prontuario TEXT,
            categorias TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # Tabela de pagamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            descricao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # Tabela de caixa (entradas e saídas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)

    # Tabela do valor inicial do caixa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valor_inicial (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            valor REAL NOT NULL
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO valor_inicial (id, valor) VALUES (1, 0.0)")

    conn.commit()