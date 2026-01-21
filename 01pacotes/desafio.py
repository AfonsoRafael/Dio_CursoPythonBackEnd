"""
SISTEMA BANCÁRIO SIMPLES EM PYTHON
---------------------------------
Este projeto demonstra o uso de:
- Programação Orientada a Objetos (POO)
- Classes abstratas
- Iteradores (__iter__ e __next__)
- Geradores (yield)
- Decoradores
- Encapsulamento
- Herança
"""

import textwrap
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

ROOT_PATH = Path(__file__).parent


# ======================================================
# ITERADOR DE CONTAS
# ======================================================
class ContasIterador:
    """
    Classe responsável por permitir que uma lista de contas
    seja percorrida usando um laço for.

    Exemplo de uso:
        for conta in ContasIterador(contas):
            print(conta)

    Para isso, a classe implementa:
    - __iter__()  → retorna o próprio iterador
    - __next__()  → retorna o próximo item
    """

    def __init__(self, contas):
        # Recebe a lista de contas que será iterada
        self.contas = contas

        # Índice interno que controla a posição atual da iteração
        self._index = 0

    def __iter__(self):
        """
        Método chamado quando o Python executa iter(objeto).
        Ele deve retornar um objeto iterável.
        """
        return self

    def __next__(self):
        """
        Método chamado a cada iteração do for.
        Retorna UMA conta por vez.
        """
        try:
            # Obtém a conta atual usando o índice
            conta = self.contas[self._index]

            # Retorna uma string formatada com os dados da conta
            return f"""
Agência:\t{conta.agencia}
Número:\t\t{conta.numero}
Titular:\t{conta.cliente.nome}
Saldo:\t\tR$ {conta.saldo:.2f}
"""
        except IndexError:
            # Quando não há mais itens, o Python encerra o for
            raise StopIteration
        finally:
            # Avança o índice independentemente do resultado
            self._index += 1


# ======================================================
# CLIENTE
# ======================================================
class Cliente:
    """
    Classe base para qualquer tipo de cliente.
    Ela NÃO sabe se o cliente é pessoa física ou jurídica.
    """

    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        """
        Executa uma transação (saque ou depósito) em uma conta.

        Este método:
        - controla o limite de transações diárias
        - delega a execução para o objeto Transacao
        """

        # Limite diário de transações
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("\n@@@ Limite diário de transações excedido! @@@")
            return

        # Registra a transação na conta
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """Associa uma nova conta ao cliente"""
        self.contas.append(conta)


# ======================================================
# PESSOA FÍSICA
# ======================================================
class PessoaFisica(Cliente):
    """
    Especialização da classe Cliente para Pessoa Física.
    """

    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ({self.cpf})>"


# ======================================================
# CONTA
# ======================================================
class Conta:
    """
    Classe base para qualquer tipo de conta bancária.
    """

    def __init__(self, numero, cliente):
        self._saldo = 0  # Saldo protegido (encapsulado)
        self._numero = numero  # Número da conta
        self._agencia = "0001"  # Agência fixa
        self._cliente = cliente  # Dono da conta
        self._historico = Historico()  # Histórico de transações

    @classmethod
    def nova_conta(cls, cliente, numero):
        """
        Método de fábrica.
        Facilita a criação de novas contas.
        """
        return cls(numero, cliente)

    @property
    def saldo(self):
        """Permite acesso somente leitura ao saldo"""
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        """
        Realiza um saque se o valor for válido e houver saldo.
        """
        if valor <= 0:
            print("\n@@@ Valor inválido! @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente! @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        """
        Realiza um depósito se o valor for positivo.
        """
        if valor <= 0:
            print("\n@@@ Valor inválido! @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


# ======================================================
# CONTA CORRENTE
# ======================================================
class ContaCorrente(Conta):
    """
    Especialização da classe Conta.
    Possui limite e quantidade máxima de saques.
    """

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        """
        Sobrescreve o método sacar da classe Conta,
        adicionando regras específicas.
        """

        # Conta quantos saques já foram feitos
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == "Saque"]
        )

        if valor > self._limite:
            print("\n@@@ Limite de saque excedido! @@@")
            return False

        if numero_saques >= self._limite_saques:
            print("\n@@@ Limite de saques excedido! @@@")
            return False

        # Chama o saque da classe pai
        return super().sacar(valor)

    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}','{self.numero}','{self.cliente.nome}')>"


# ======================================================
# HISTÓRICO
# ======================================================
class Historico:
    """
    Armazena todas as transações realizadas em uma conta.
    """

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        """Retorna todas as transações"""
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """
        Adiciona uma transação ao histórico.
        """
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo=None):
        """
        GERADOR DE TRANSAÇÕES

        Usa yield para retornar UMA transação por vez,
        economizando memória.
        """
        for transacao in self._transacoes:
            if tipo is None or transacao["tipo"].lower() == tipo.lower():
                yield transacao

    def transacoes_do_dia(self):
        """
        Retorna apenas as transações feitas no dia atual.
        """
        hoje = datetime.now().date()
        return [
            t
            for t in self._transacoes
            if datetime.strptime(t["data"], "%d-%m-%Y %H:%M:%S").date() == hoje
        ]


# ======================================================
# TRANSAÇÃO (CLASSE ABSTRATA)
# ======================================================
class Transacao(ABC):
    """
    Classe abstrata que define o contrato das transações.
    """

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    """Transação do tipo saque"""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """Transação do tipo depósito"""

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


# ======================================================
# DECORADOR
# ======================================================
def log_transacao(func):
    """
    Decorador que registra quando uma função é executada.
    """

    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        # utcnow esta sendo descontinuada, nova forma é usar o timezone
        data_hora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with open(ROOT_PATH / "log.txt", "a", encoding="utf-8", newline="") as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__}' executada com argumentos {args}\
                     e {kwargs}. Retornou {resultado}\n"
            )

        return resultado

    return wrapper


# ======================================================
# FUNÇÕES DO SISTEMA
# ======================================================
def menu():
    """Exibe o menu e retorna a opção escolhida"""
    texto = """
================ MENU ================
[d] Depositar
[s] Sacar
[e] Extrato
[nc] Nova conta
[lc] Listar contas
[nu] Novo usuário
[q] Sair
=> """
    return input(textwrap.dedent(texto))


def filtrar_cliente(cpf, clientes):
    """Busca um cliente pelo CPF"""
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None


def recuperar_conta_cliente(cliente):
    """Retorna a primeira conta do cliente"""
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None
    return cliente.contas[0]


@log_transacao
def depositar(clientes):
    cpf = input("CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Valor do depósito: "))
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, Deposito(valor))


@log_transacao
def sacar(clientes):
    cpf = input("CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Valor do saque: "))
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, Saque(valor))


@log_transacao
def exibir_extrato(clientes):
    cpf = input("CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n========== EXTRATO ==========")
    for t in conta.historico.gerar_relatorio():
        print(f"{t['data']} - {t['tipo']} - R$ {t['valor']:.2f}")

    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("=============================")


@log_transacao
def criar_cliente(clientes):
    cpf = input("CPF: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Cliente já existe! @@@")
        return

    nome = input("Nome: ")
    data_nascimento = input("Data de nascimento: ")
    endereco = input("Endereço: ")

    clientes.append(PessoaFisica(nome, data_nascimento, cpf, endereco))
    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero, clientes, contas):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = ContaCorrente(numero, cliente)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    """Lista todas as contas usando o iterador"""
    for conta in ContasIterador(contas):
        print("=" * 60)
        print(conta)


# ======================================================
# FUNÇÃO PRINCIPAL
# ======================================================
def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(len(contas) + 1, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("\n@@@ Opção inválida! @@@")


main()
