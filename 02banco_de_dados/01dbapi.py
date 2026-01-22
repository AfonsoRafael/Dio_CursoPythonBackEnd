import sqlite3
from pathlib import Path

ROOT_PATH = Path(__file__).parent


conexao = sqlite3.connect(ROOT_PATH / "banco_teste.db")
cursor = conexao.cursor()
cursor.row_factory = sqlite3.Row # Faz retornar um dicionario

def criar_tabela(conexao, cursor):
    cursor.execute("CREATE TABLE cliente(id INTEGER PRIMARY KEY AUTOINCREMENT, nome VARCHAR(100), email VARCHAR(150))")
    conexao.commit()

def inserir_registro(conexao, cursor, nome, email):
    data = (nome,email) # Forma segura de enviar os dados, Tupla
    cursor.execute("INSERT INTO cliente (nome, email) VALUES (?,?);",data)
    conexao.commit() # So envia com commit

def atualizar_registro(conexao, cursor, nome, email, id):
    data = (nome,email, id)
    cursor.execute("UPDATE cliente SET nome=?, email=? WHERE id=?;",data)
    conexao.commit()

def excluir_registro(conexao, cursor, id):
    data = (id,) # Virgula no final para significar tupla
    cursor.execute("DELETE FROM cliente WHERE id=?;", data)
    conexao.commit()

def inserir_muitos(conexao, cursor, dados):
    cursor.executemany("INSERT INTO cliente (nome, email) VALUES (?,?)", dados)
    conexao.commit()    

def recuperar_cliente(cursor, id):
    cursor.execute("SELECT nome FROM cliente WHERE id=?", (id,))
    return cursor.fetchone() # Retorna so um valor

def listar_clientes(cursor):
    return cursor.execute("SELECT nome FROM cliente;")

clientes = listar_clientes(cursor)
for nome in clientes:
    print(dict(nome))

cliente = recuperar_cliente(cursor, 1)
print(dict(cliente))
print(f"O cliente e {cliente['nome']}") # Excelente para deixar o codigo legivel


# Para inserir multiplos dados faz uma lista de tuplas
# é interessante pois faz 1 commit e economiza recursos do sistema
# dados = [
#     ("Jose","jose@gemail.com"),
#     ("Augusto","augusto@gemail.com"),
#     ("Maria","maria@gemail.com"),
#     ("Mariana","mariana@gemail.com"),
#     ]
# inserir_muitos(conexao, cursor, dados)