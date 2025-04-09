import sqlite3

conn = sqlite3.connect("banco_dados.db")
cursor = conn.cursor()

# Adiciona a coluna 'ativo' com valor padrão 1 (ativo)
try:
    cursor.execute("ALTER TABLE clientes ADD COLUMN ativo INTEGER DEFAULT 1")
    print("Coluna 'ativo' adicionada.")
except sqlite3.OperationalError:
    print("Coluna 'ativo' já existe.")

conn.commit()
conn.close()
