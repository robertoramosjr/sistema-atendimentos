import sqlite3

conn = sqlite3.connect("banco_dados.db")
cursor = conn.cursor()

# Adiciona a coluna de frequência, se ainda não existir
try:
    cursor.execute("ALTER TABLE clientes ADD COLUMN frequencia TEXT DEFAULT 'Semanal'")
    print("Coluna 'frequencia' adicionada com sucesso.")
except sqlite3.OperationalError:
    print("Coluna 'frequencia' já existe.")

conn.commit()
conn.close()
