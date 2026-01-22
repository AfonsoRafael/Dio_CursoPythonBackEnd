import sqlite3
from pathlib import Path

ROOT_PATH = Path(__file__).parent


conexao = sqlite3.connect(ROOT_PATH / "banco_teste.db")
cursor = conexao.cursor()
cursor.row_factory = sqlite3.Row # Faz retornar um dicionario

try:
    cursor.execute("INSERT INTO cliente (nome, email) VALUES (?,?)",("teste1","teste1@gmail.com"))
    cursor.execute("INSERT INTO cliente (id,nome, email) VALUES (?,?,?)",(1,"teste1","teste1@gmail.com"))
    conexao.commit()
except Exception as exc:
        print(f"Ops, ocoreu um erro: {exc}")
        conexao.rollback()# Cancela toda a operação por causa de um erro
