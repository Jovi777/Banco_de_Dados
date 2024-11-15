import mysql.connector
from mysql.connector import Error

# Usado para conectar ao banco de dados
def conectar_banco(): 
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1826',
            database='trabalho'
        )
        if conexao.is_connected():
            return conexao
        else:
            print("Erro ao conectar ao banco de dados.")
            return None
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def inserir_associacao(cursor, tipo):
    """Função para inserir dados na tabela associacoes_esportivas"""
    sigla = input("Digite a sigla da associação (3 caracteres): ").upper()
    apelido = input("Digite o apelido da associação: ").title()

    # Validação do valor de qualidade
    while True:
        try:
            qualidade = float(input("Digite a qualidade da associação (0.00 a 5.00): "))
            if 0.00 <= qualidade <= 5.00:
                qualidade = round(qualidade, 2)
                break
            else:
                print("Qualidade deve estar entre 0.00 e 5.00.")
        except ValueError:
            print("Por favor, insira um número válido para a qualidade.")

    nome = input("Digite o nome da associação: ").title()
    mascote = input("Digite o mascote da associação: ").title()
    formacao = input("Digite a formação da associação: ").upper()
    tipo_associacao = tipo

    # Comando SQL para inserção de dados na tabela associacoes_esportivas
    sql_associacao = """
        INSERT INTO associacoes_esportivas (sigla, apelido, qualidade, nome, mascote, formacao, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores_associacao = (sigla, apelido, qualidade, nome, mascote, formacao, tipo_associacao)

    # Executa o comando de inserção
    cursor.execute(sql_associacao, valores_associacao)
    print("Associação esportiva inserida com sucesso!")
    return cursor.lastrowid  # Retorna o ID da associação inserida

def inserir_clube(cursor, id_associacao_inserido, conexao):
    """Função para inserir dados do clube, incluindo a cidade"""
    receita_em_mi = float(input("Digite a receita do clube em milhoes: "))
    cidade_nome = input("Digite o nome da cidade onde o clube está localizado: ").title()
    pais = input("Digite o país onde o clube está localizado: ").title()

    # Verifica se a cidade já existe
    id_cidade_inserida = inserir_cidade(cursor, cidade_nome, conexao)

    # Comando SQL para inserir dados na tabela clubes
    sql_clube = """
        INSERT INTO clubes (id_associacao, receita_em_mi, id_cidade, pais)
        VALUES (%s, %s, %s, %s)
    """
    valores_clube = (id_associacao_inserido, receita_em_mi, id_cidade_inserida, pais)

    # Executa o comando para inserir o clube
    cursor.execute(sql_clube, valores_clube)
    conexao.commit()  # Não se esqueça de fazer o commit na conexão
    print("Clube inserido com sucesso!")

def inserir_selecao(cursor, id_associacao_inserido):
    """Função para inserir dados de uma seleção"""
    # Para seleções, não há dados adicionais a serem inseridos além do ID da associação.
    sql_selecao = """
        INSERT INTO selecoes (id_associacao)
        VALUES (%s)
    """
    cursor.execute(sql_selecao, (id_associacao_inserido,))
    print("Seleção inserida com sucesso!")

def inserir_cidade(cursor, cidade_nome, conexao):
    """Função para verificar e inserir uma cidade, se necessário"""
    # Verifica se a cidade já existe na tabela cidades
    cursor.execute("SELECT id_cidade FROM cidades WHERE nome = %s", (cidade_nome,))
    cidade = cursor.fetchone()

    if cidade is None:  # Se a cidade não existe, insere a cidade
        print(f"A cidade '{cidade_nome}' não foi encontrada. Inserindo no banco de dados...")
        cursor.execute("INSERT INTO cidades (nome) VALUES (%s)", (cidade_nome,))
        conexao.commit()  # Confirma a inserção da cidade
        # Obtém o ID da cidade recém-inserida
        id_cidade_inserida = cursor.lastrowid
        print(f"Cidade '{cidade_nome}' inserida com sucesso!")
        return id_cidade_inserida
    else:
        # Se a cidade já existe, utiliza o ID da cidade encontrada
        id_cidade_inserida = cidade[0]
        print(f"A cidade '{cidade_nome}' já existe no banco de dados.")
        return id_cidade_inserida

def inserir_jogador(cursor):
    """Função para inserir dados de um jogador"""
    selecao_nome = input("Digite o nome da seleção: ").title()

    # Verifica se a seleção existe no banco de dados
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (selecao_nome,))
    selecao = cursor.fetchone()

    if selecao is None:
        print(f"A seleção '{selecao_nome}' não existe no banco de dados. Vamos adicionar a seleção.")
        # Inserir a seleção, já que não existe
        id_associacao_inserido = inserir_associacao(cursor, tipo="selecao")
        inserir_selecao(cursor, id_associacao_inserido)
        selecao = (id_associacao_inserido,)  # Atualiza o ID da seleção

    # A partir do ID da seleção, podemos inserir o jogador
    nome = input("Digite o nome do jogador: ").title()

    # Validação da posição do jogador
    posicoes_validas = ["GOL", "ZAG", "LE", "LD", "ADE", "ADD", "VOL", "MC", "ME", "MD", "MEI", "PD", "PE", "SA", "ATA"]
    while True:
        posicao = input("Digite a posição do jogador: ").upper()
        if posicao in posicoes_validas:
            break
        else:
            print("Posição inválida! Por favor, escolha uma posição válida.")

    # Comando SQL para inserir dados na tabela jogadores
    sql_jogador = """
        INSERT INTO jogadores (id_selecao, nome, posicao)
        VALUES (%s, %s, %s)
    """
    valores_jogador = (selecao[0], nome, posicao)

    # Executa o comando para inserir o jogador
    cursor.execute(sql_jogador, valores_jogador)
    print(f"Jogador '{nome}' inserido com sucesso na seleção '{selecao_nome}'!")

def inserir_estadio_a_clube(cursor, conexao):
    """Função para inserir um estádio e associá-lo a um clube"""
    
    # Perguntar o nome do estádio e do clube
    nome_estadio = input("Digite o nome do estádio: ").title()
    nome_clube = input("Digite o nome do clube ao qual o estádio será atrelado: ").title()

    # Passo 1: Verificar se o estádio existe, se não, criar
    cursor.execute("SELECT id_estadio FROM estadios WHERE nome = %s", (nome_estadio,))
    estadio = cursor.fetchone()

    if estadio is None:
        print(f"O estádio '{nome_estadio}' não existe. Vamos criá-lo.")
        # Se o estádio não existir, criá-lo
        inserir_estadio(cursor, nome_estadio)

    # Passo 2: Verificar se o clube existe, se não, criar
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (nome_clube,))
    clube = cursor.fetchone()

    if clube is None:
        print(f"O clube '{nome_clube}' não existe. Vamos criá-lo.")
        # Se o clube não existir, criá-lo
        id_associacao_inserido = inserir_associacao(cursor, tipo="clube")
        inserir_clube(cursor, id_associacao_inserido, conexao)  # Passar conexao para inserir_clube

    # Obter id do estádio recém-criado (ou já existente)
    cursor.execute("SELECT id_estadio FROM estadios WHERE nome = %s", (nome_estadio,))
    estadio = cursor.fetchone()
    
    # Obter id do clube recém-criado (ou já existente)
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (nome_clube,))
    clube = cursor.fetchone()

    # Associar o estádio ao clube na tabela clube_estadios
    sql_associacao = """
        INSERT INTO clube_estadios (id_estadio, id_associacao)
        VALUES (%s, %s)
    """
    valores_associacao = (estadio[0], clube[0])

    cursor.execute(sql_associacao, valores_associacao)
    conexao.commit()  # Confirma a associação no banco de dados
    print(f"O estádio '{nome_estadio}' foi associado com sucesso ao clube '{nome_clube}'!")

def inserir_estadio(cursor, nome_estadio):
    """Função para criar apenas um estádio"""
    
    while True:
        try:
            capacidade = int(input("Digite a capacidade do estádio (entre 1000 e 100000): "))
            if 1000 <= capacidade <= 100000:
                break
            else:
                print("Capacidade inválida! Deve estar entre 1000 e 100000.")
        except ValueError:
            print("Por favor, insira um número válido para a capacidade.")

    # Inserir o estádio na tabela estadios
    sql_estadio = """
        INSERT INTO estadios (nome, capacidade)
        VALUES (%s, %s)
    """
    valores_estadio = (nome_estadio, capacidade)
    cursor.execute(sql_estadio, valores_estadio)
    print(f"O estádio '{nome_estadio}' foi criado com sucesso!")


# possiveis funções:
'''
Inserir estadio, atrelar estadio a um clube FEITO
Inserir contrato, atrelar jogador a um clube 
Inserir Atributos, atribuir atributos ao jogador
Inserir Estilo de jogo, atribuir estilo de jogo ao jogador
Inserir Campeonatos, adicionar campeonato
Inserir times em campeonatos, add time e campeonato caso ñ existam
Inserir estatisticas, add campeonato e add jogador
Inserir partidas, add clubes e campeonatos e add clubes aos campeonatos caso campeonato not null
Inserir Funcionarios, adicionar cargo caso não exista, adicionar nacionalidade caso não exista e add clube

Funções para alterar tudo isso

Funções para excluir esses registros

Funções para consultar alguns registros

'''

def menu():
    """Exibe o menu interativo"""
    while True:
        print("\nMENU:")
        print("1 - Inserir Clube")
        print("2 - Inserir Selecao")
        print("3 - Inserir Jogador")
        print("4 - Inserir Estadio")
        print("5 - Atrelar Estadio a um clube")
        print("6 - X")
        print("7 - X")
        print("8 - X")
        print("9 - X")
        print("X - Sair")

        escolha = input("Escolha a opção: ")

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                # Inserir clube
                id_associacao_inserido = inserir_associacao(cursor, tipo="clube")
                inserir_clube(cursor, id_associacao_inserido, conexao)
            elif escolha == "2":
                # Inserir seleção
                id_associacao_inserido = inserir_associacao(cursor, tipo="selecao")
                inserir_selecao(cursor, id_associacao_inserido)
            elif escolha == "3":
                # Inserir jogador
                inserir_jogador(cursor)
            elif escolha == "4":
                # Inserir estadio
                nome_estadio = input("Digite o nome do estadio: ").title()
                inserir_estadio(cursor, nome_estadio)
            elif escolha == "5":
                # Atrelar estadio a um clube
                inserir_estadio_a_clube(cursor, conexao)
            elif escolha == "6":
                print("Função em desenvolvimento.")
            elif escolha == "7":
                print("Função em desenvolvimento.")
            elif escolha == "8":
                print("Função em desenvolvimento.")
            elif escolha == "9":
                print("Função em desenvolvimento.")
            else:
                print("Saindo do programa...")
                break

            conexao.commit()  # Confirma todas as alterações no banco
            cursor.close()
            conexao.close()

if __name__ == "__main__":
    menu()
