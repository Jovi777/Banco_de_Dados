import mysql.connector
from mysql.connector import Error
#usado para conectar ao banco de dados
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

def inserir_associacao(cursor):
    """Função para inserir dados na tabela associacoes_esportivas"""
    sigla = input("Digite a sigla da associação (3 caracteres): ")
    apelido = input("Digite o apelido da associação: ")

    # Validação do valor de qualidade
    while True:
        try:
            qualidade = float(input("Digite a qualidade da associação (0.00 a 5.00): "))
            if 0.00 <= qualidade <= 5.00:
                qualidade = round(qualidade, 2)  # Limita a duas casas decimais
                break
            else:
                print("Qualidade deve estar entre 0.00 e 5.00.")
        except ValueError:
            print("Por favor, insira um número válido para a qualidade.")

    nome = input("Digite o nome da associação: ")
    mascote = input("Digite o mascote da associação: ")
    formacao = input("Digite a formação da associação: ")
    tipo = input("A associação é uma selecao ou um clube? (Digite 'clube' ou 'selecao'): ")

    # Comando SQL para inserção de dados na tabela associacoes_esportivas
    sql_associacao = """
        INSERT INTO associacoes_esportivas (sigla, apelido, qualidade, nome, mascote, formacao, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores_associacao = (sigla, apelido, qualidade, nome, mascote, formacao, tipo)

    # Executa o comando de inserção
    cursor.execute(sql_associacao, valores_associacao)
    print("Associação esportiva inserida com sucesso!")
    return cursor.lastrowid  # Retorna o ID da associação inserida

def inserir_clube(cursor, id_associacao_inserido, conexao):
    """Função para inserir dados do clube, incluindo a cidade"""
    receita = float(input("Digite a receita do clube: "))
    cidade_nome = input("Digite o nome da cidade onde o clube está localizado: ")
    pais = input("Digite o país onde o clube está localizado: ")

    # Verifica se a cidade já existe
    id_cidade_inserida = inserir_cidade(cursor, cidade_nome, conexao)

    # Comando SQL para inserir dados na tabela clubes
    sql_clube = """
        INSERT INTO clubes (id_associacao, receita, id_cidade, pais)
        VALUES (%s, %s, %s, %s)
    """
    valores_clube = (id_associacao_inserido, receita, id_cidade_inserida, pais)

    # Executa o comando para inserir o clube
    cursor.execute(sql_clube, valores_clube)
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

def menu():
    """Exibe o menu interativo"""
    while True:
        print("\nMENU:")
        print("1 - Inserir Clube")
        print("2 - Inserir Selecao")
        print("3 - Inserir Jogador")
        print("4 - Alterar Clube")
        print("5 - Alterar Selecao")
        print("6 - Alterar Jogador")
        print("7 - Deletar Clube")
        print("8 - Deletar Associacao")
        print("9 - Deletar Jogador")
        print("X - Sair")

        escolha = input("Escolha a opção: ")

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                # Inserir clube
                id_associacao_inserido = inserir_associacao(cursor)
                inserir_clube(cursor, id_associacao_inserido, conexao)
            elif escolha == "2":
                # Inserir seleção
                id_associacao_inserido = inserir_associacao(cursor)
                inserir_selecao(cursor, id_associacao_inserido)
            elif escolha == "3":
                print("Função em desenvolvimento.")
            elif escolha == "4":
                print("Função em desenvolvimento.")
            elif escolha == "5":
                print("Função em desenvolvimento.")
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
