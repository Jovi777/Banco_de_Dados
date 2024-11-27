from tabulate import tabulate
#pip install tabulate
import mysql.connector
from mysql.connector import Error
#testes:
def inserir_atributos(cursor):
    """Insere os atributos de um jogador no banco de dados com verificação de intervalo (0-100), buscando ID e posição do jogador no banco."""
    
    # Pergunta o nome do jogador
    nome_jogador = input("Digite o nome do jogador: ").strip()

    # Consulta o ID e a posição do jogador a partir do nome
    cursor.execute("SELECT id_jogador, posicao FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado!")
        return

    id_jogador, posicao = jogador
    posicao = posicao.strip().upper()  # Garante que a posição seja em maiúsculas

    def pedir_atributo(nome_atributo):
        """Função auxiliar para pedir atributos e verificar se estão entre 0 e 100."""
        while True:
            try:
                valor = float(input(f"Digite o atributo de {nome_atributo} (0-100): "))
                if 0 <= valor <= 100:
                    return valor
                else:
                    print("Valor inválido! O valor deve estar entre 0 e 100.")
            except ValueError:
                print("Valor inválido! Por favor, insira um número válido.")

    # Se o jogador for goleiro, mudamos os nomes dos atributos
    if posicao == "GOL":
        print("\nAtributos para Goleiro:")
        ritmo = pedir_atributo("elasticidade")
        chute = pedir_atributo("manuseio") 
        passe = pedir_atributo("chute") 
        drible = pedir_atributo("reflexos")
        defesa = pedir_atributo("velocidade")  
        fisico = pedir_atributo("posicionamento") 
    else:
        # Para outras posições, mantemos os nomes originais dos atributos
        print("\nAtributos para Jogador de Campo:")
        ritmo = pedir_atributo("ritmo")
        chute = pedir_atributo("chute")
        passe = pedir_atributo("passe")
        drible = pedir_atributo("drible")
        defesa = pedir_atributo("defesa")
        fisico = pedir_atributo("físico")

    # Insere os atributos na tabela atributos
    cursor.execute("""
        INSERT INTO atributos (id_jogador, ritmo, chute, passe, drible, defesa, fisico)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (id_jogador, ritmo, chute, passe, drible, defesa, fisico))

    print("Atributos inseridos com sucesso!")

    # Atualiza o geral após a inserção dos atributos
    atualizar_geral(cursor, id_jogador, posicao)

def alterar_atributos(cursor):
    """Atualiza os atributos de um jogador no banco de dados com verificação de intervalo (0-100), buscando ID e posição do jogador no banco."""
    
    # Pergunta o nome do jogador
    nome_jogador = input("Digite o nome do jogador para atualizar os atributos: ").strip()

    # Consulta o ID e a posição do jogador a partir do nome
    cursor.execute("SELECT id_jogador, posicao FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado!")
        return

    id_jogador, posicao = jogador
    posicao = posicao.strip().upper()  # Garante que a posição seja em maiúsculas

    def pedir_atributo(nome_atributo):
        """Função auxiliar para pedir atributos e verificar se estão entre 0 e 100."""
        while True:
            try:
                valor = float(input(f"Digite o novo atributo de {nome_atributo} (0-100): "))
                if 0 <= valor <= 100:
                    return valor
                else:
                    print("Valor inválido! O valor deve estar entre 0 e 100.")
            except ValueError:
                print("Valor inválido! Por favor, insira um número válido.")

    # Se o jogador for goleiro, mudamos os nomes dos atributos
    if posicao == "GOL":
        print("\nAtributos para Goleiro:")
        ritmo = pedir_atributo("elasticidade")
        chute = pedir_atributo("manuseio") 
        passe = pedir_atributo("chute")  
        drible = pedir_atributo("reflexos")
        defesa = pedir_atributo("velocidade") 
        fisico = pedir_atributo("posicionamento")
    else:
        # Para outras posições, mantemos os nomes originais dos atributos
        print("\nAtributos para Jogador de Campo:")
        ritmo = pedir_atributo("ritmo")
        chute = pedir_atributo("chute")
        passe = pedir_atributo("passe")
        drible = pedir_atributo("drible")
        defesa = pedir_atributo("defesa")
        fisico = pedir_atributo("físico")

    # Atualiza os atributos no banco de dados
    cursor.execute("""
        UPDATE atributos
        SET ritmo = %s, chute = %s, passe = %s, drible = %s, defesa = %s, fisico = %s
        WHERE id_jogador = %s
    """, (ritmo, chute, passe, drible, defesa, fisico, id_jogador))

    print("Atributos atualizados com sucesso!")

    # Recalcular e atualizar o valor 'geral' após atualização
    atualizar_geral(cursor, id_jogador, posicao)

def atualizar_geral(cursor, id_jogador, posicao):
    """Calcula e atualiza o valor 'geral' do jogador no banco de dados."""
    
    geral = calcular_geral(cursor, id_jogador, posicao)
    
    if geral is not None:
        geral = round(geral)
        cursor.execute("""
            UPDATE atributos
            SET geral = %s
            WHERE id_jogador = %s
        """, (geral, id_jogador))
        print(f"Geral do jogador atualizado para {geral}.")

def calcular_geral(cursor, id_jogador, posicao):
    """Calcula o valor geral do jogador com base em seus atributos e posição."""
    
    # Primeiro, buscamos os atributos do jogador
    cursor.execute("""
        SELECT drible, ritmo, fisico, passe, chute, defesa
        FROM atributos
        WHERE id_jogador = %s
    """, (id_jogador,))
    atributos = cursor.fetchone()
    
    if not atributos:
        print("Atributos não encontrados para o jogador.")
        return None
    
    drible, ritmo, fisico, passe, chute, defesa = map(float, atributos)
    
    # Atribuindo pesos para cada posição
    if posicao in ['ATA', 'SA']:  # Atacantes
        peso_ritmo = 1.2
        peso_chute = 1.7
        peso_fisico = 1.5
        peso_defesa = 0.1
        peso_passe = 1.0
        peso_drible = 1.0

    elif posicao in ['PE', 'PD', 'ME', 'MD']:  # Pontas
        peso_ritmo = 1.5
        peso_chute = 1.0
        peso_fisico = 1.0
        peso_defesa = 0.5
        peso_passe = 1.0
        peso_drible = 1.5

    elif posicao in ['MEI']:  # Meias ofensivo
        peso_ritmo = 1.0
        peso_chute = 1.0
        peso_fisico = 1.0
        peso_defesa = 0.5
        peso_passe = 1.5
        peso_drible = 1.5
    
    elif posicao in ['MC']:  # Meias
        peso_ritmo = 1.0
        peso_chute = 1.0
        peso_fisico = 1.0
        peso_defesa = 0.7
        peso_passe = 1.5
        peso_drible = 1.3
    
    elif posicao in ['VOL']:  # Volantes
        peso_ritmo = 1.0
        peso_chute = 0.8
        peso_fisico = 1.0
        peso_defesa = 1.5
        peso_passe = 1.2
        peso_drible = 0.5
    
    elif posicao in ['LE', 'LD', 'ADE', 'ADD']:  # Laterais
        peso_ritmo = 1.2
        peso_chute = 0.5
        peso_fisico = 1.0
        peso_defesa = 1.5
        peso_passe = 1.3
        peso_drible = 1.0
    
    elif posicao in ['ZAG']:  # zagueiros
        peso_ritmo = 0.5
        peso_chute = 0.2
        peso_passe = 0.5
        peso_drible = 0.5
        peso_defesa = 2.8
        peso_fisico = 2.0
    
    elif posicao in ['GOL']:  # goleiros
        peso_ritmo = 1.2
        peso_chute = 1.5
        peso_passe = 0.5
        peso_drible = 1.5
        peso_defesa = 0.5
        peso_fisico = 1.3

    # Calculando o "geral" ponderado
    geral = (
        (drible * peso_drible) +
        (ritmo * peso_ritmo) +
        (fisico * peso_fisico) +
        (passe * peso_passe) +
        (chute * peso_chute) +
        (defesa * peso_defesa)
    ) / ((peso_passe + peso_ritmo + peso_chute + peso_fisico + peso_defesa + peso_drible)-0.5)

    return round(geral)

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

def inserir_campeonato(cursor, conexao):
    """Função para inserir dados de um campeonato"""
    nome_campeonato = input("Digite o nome do campeonato: ").title()

    # Verificar se o campeonato já existe no banco de dados
    cursor.execute("SELECT id_campeonato FROM campeonatos WHERE nome = %s", (nome_campeonato,))
    campeonato = cursor.fetchone()

    if campeonato:
        print(f"O campeonato '{nome_campeonato}' já existe no banco de dados com o ID {campeonato[0]}.")
        return

    # Caso o campeonato não exista, insira-o
    sql_campeonato = """
        INSERT INTO campeonatos (nome)
        VALUES (%s)
    """
    cursor.execute(sql_campeonato, (nome_campeonato,))
    conexao.commit()  # Confirma a inserção no banco de dados
    print(f"Campeonato '{nome_campeonato}' inserido com sucesso!")

def inserir_associacoes_campeonato(cursor, conexao, nome_campeonato):
    """Função para associar clubes ou seleções a um campeonato pelo nome"""

    # Buscar o ID do campeonato pelo nome
    cursor.execute("SELECT id_campeonato FROM campeonatos WHERE nome = %s", (nome_campeonato,))
    campeonato = cursor.fetchone()

    if not campeonato:
        print(f"Erro: O campeonato '{nome_campeonato}' não existe. Tente novamente.")
        return  # Sai da função se o campeonato não existir

    id_campeonato = campeonato[0]
    print(f"Associando clubes ou seleções ao campeonato '{nome_campeonato}' (ID {id_campeonato}).")

    while True:
        nome_associacao = input("Digite o nome da associação (ou 'sair' para encerrar): ").title()
        if nome_associacao.lower() == "sair":
            break

        # Verifica se a associação existe
        cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s", (nome_associacao,))
        associacao = cursor.fetchone()

        if associacao is None:
            print(f"A associação '{nome_associacao}' não existe no banco de dados. Tente novamente.")
            continue

        # Verifica se a associação já está vinculada ao campeonato
        cursor.execute("""
            SELECT * FROM campeonatos_associacoes 
            WHERE id_campeonato = %s AND id_associacao = %s
        """, (id_campeonato, associacao[0]))
        existente = cursor.fetchone()

        if existente:
            print(f"A associação '{nome_associacao}' já está vinculada ao campeonato.")
            continue

        # Insere a associação no campeonato com uma classificação inicial
        classificacao = int(input(f"Digite a classificação inicial para '{nome_associacao}': "))
        cursor.execute("""
            INSERT INTO campeonatos_associacoes (id_campeonato, id_associacao, classificacao)
            VALUES (%s, %s, %s)
        """, (id_campeonato, associacao[0], classificacao))
        conexao.commit()
        print(f"Associação '{nome_associacao}' vinculada ao campeonato '{nome_campeonato}' com sucesso!")

def inserir_partidas_campeonato(cursor, conexao, nome_campeonato):
    """Função para registrar partidas em um campeonato pelo nome"""

    # Buscar o ID do campeonato pelo nome
    cursor.execute("SELECT id_campeonato FROM campeonatos WHERE nome = %s", (nome_campeonato,))
    campeonato = cursor.fetchone()

    if not campeonato:
        print(f"Erro: O campeonato '{nome_campeonato}' não existe. Tente novamente.")
        return  # Sai da função se o campeonato não existir

    id_campeonato = campeonato[0]
    print(f"Registrando partidas para o campeonato '{nome_campeonato}' (ID {id_campeonato}).")

    while True:
        adicionar = input("Deseja adicionar uma partida ao campeonato? (s/n): ").lower()
        if adicionar == "n":
            break

        # Solicitar os nomes das associações envolvidas
        nome_mandante = input("Digite o nome da associação mandante: ").title()
        nome_visitante = input("Digite o nome da associação visitante: ").title()

        # Verificar se as associações existem
        cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s", (nome_mandante,))
        mandante = cursor.fetchone()
        cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s", (nome_visitante,))
        visitante = cursor.fetchone()

        if not mandante or not visitante:
            print(f"Erro: Uma das associações ('{nome_mandante}' ou '{nome_visitante}') não existe no banco de dados. Tente novamente.")
            continue

        # Solicitar os dados da partida
        resultado = input("Digite o resultado da partida (Ex.: 2-1): ")
        tempo = input("Digite o tempo de jogo (HH:MM:SS): ")

        # Inserir a partida no banco de dados
        sql_partida = """
            INSERT INTO partidas (id_campeonato, id_mandante, id_visitante, resultado, tempo)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores_partida = (id_campeonato, mandante[0], visitante[0], resultado, tempo)
        cursor.execute(sql_partida, valores_partida)
        conexao.commit()
        print(f"Partida entre '{nome_mandante}' e '{nome_visitante}' registrada com sucesso!")

def inserir_contrato(cursor):
    """Função para inserir contrato de um jogador em um clube"""
    # Passo 1: Obter informações do contrato
    nome_jogador = input("Digite o nome do jogador: ").title()

    # Passo 2: Verificar se o jogador existe, caso contrário, inserir o jogador
    cursor.execute("SELECT id_jogador, id_selecao FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if jogador is None:
        print(f"O jogador '{nome_jogador}' não existe. Vamos adicioná-lo.")
        inserir_jogador(cursor)  # Chama a função para inserir o jogador
        # Verifica novamente se o jogador foi inserido
        cursor.execute("SELECT id_jogador, id_selecao FROM jogadores WHERE nome = %s", (nome_jogador,))
        jogador = cursor.fetchone()
        if jogador is None:
            print("Erro: Jogador não foi inserido corretamente.")
            return  # Sai da função em caso de erro

    # Passo 3: Inserir o contrato
    salario = float(input("Digite o salário do jogador: "))
    data_inicial = input("Digite a data de início do contrato (YYYY-MM-DD): ")
    duracao = input("Digite a data de término do contrato (YYYY-MM-DD): ")

    # Tratar o valor do bônus
    while True:
        try:
            bonus_input = input("Digite o valor do bônus (0 para nenhum bônus): ").strip()
            if bonus_input == "":  # Se o usuário não inserir nada, considerar 0 como bônus
                bonus = 0.0
                break
            bonus = float(bonus_input)  # Tentar converter o valor em float
            break
        except ValueError:
            print("Por favor, insira um número válido para o bônus.")

    # Tratar o valor das luvas
    while True:
        try:
            luvas_input = input("Digite o valor das luvas (0 para nenhum valor): ").strip()
            if luvas_input == "":  # Se o usuário não inserir nada, considerar 0 como luvas
                luvas = 0.0
                break
            luvas = float(luvas_input)  # Tentar converter o valor em float
            break
        except ValueError:
            print("Por favor, insira um número válido para o valor das luvas.")

    # Verificando se a multa recisória foi informada, caso contrário, atribuir NULL
    multa_recisoria_input = input("Digite o valor da multa recisória: ").strip()
    
    # Verificando se o campo está vazio e atribuindo None se estiver
    if multa_recisoria_input == "":
        multa_recisoria = None
    elif multa_recisoria_input == '0':
        multa_recisoria = 0.0
    else:
        try:
            multa_recisoria = float(multa_recisoria_input)
        except ValueError:
            print("Valor inválido para a multa recisória. Será considerado como NULL.")
            multa_recisoria = None

    numero = int(input("Digite o número usado pelo jogador: "))

    # Passo 4: Obter o ID do clube
    clube_nome = input("Digite o nome do clube: ").title()

    # Verificar se o clube existe
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (clube_nome,))
    clube = cursor.fetchone()

    if clube is None:
        print(f"O clube '{clube_nome}' não existe. Vamos adicioná-lo.")
        id_associacao_clube = inserir_associacao(cursor, tipo="clube")  # Inserir a associação
        inserir_clube(cursor, id_associacao_clube, cursor._connection)  # Inserir o clube (passando a conexão)
        # Verifica novamente se o clube foi inserido
        cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (clube_nome,))
        clube = cursor.fetchone()
        if clube is None:
            print("Erro: Clube não foi inserido corretamente.")
            return  # Sai da função em caso de erro

    # Passo 5: Inserir o contrato
    sql_contrato = """
        INSERT INTO contratos (salario, data_inicial, duracao, bonus, luvas, multarecisoria, numero, id_jogador, id_associacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores_contrato = (salario, data_inicial, duracao, bonus, luvas, multa_recisoria, numero, jogador[0], clube[0])

    cursor.execute(sql_contrato, valores_contrato)
    print(f"Contrato de jogador '{nome_jogador}' inserido com sucesso!")

'''
def inserir_atributos(cursor):
    """Função para inserir atributos de um jogador"""
    
    # Passo 1: Solicitar o nome do jogador
    nome_jogador = input("Digite o nome do jogador: ").title()
    
    # Passo 2: Verificar se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if jogador is None:
        print(f"O jogador '{nome_jogador}' não existe no banco de dados. Vamos adicioná-lo.")
        # Chama a função para inserir o jogador
        inserir_jogador(cursor)
        
        # Após a inserção, tentamos localizar novamente o jogador
        cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
        jogador = cursor.fetchone()

        if jogador is None:
            print("Erro: Jogador não foi inserido corretamente.")
            return  # Sai da função caso o jogador ainda não tenha sido inserido corretamente
    
    # Passo 3: Coletar os atributos do jogador
    while True:
        try:
            drible = float(input("Digite o valor de drible (0 a 100): "))
            if 0 <= drible <= 100:
                break
            else:
                print("Valor inválido! O drible deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o drible.")
    
    while True:
        try:
            ritmo = float(input("Digite o valor de ritmo (0 a 100): "))
            if 0 <= ritmo <= 100:
                break
            else:
                print("Valor inválido! O ritmo deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o ritmo.")
    
    while True:
        try:
            fisico = float(input("Digite o valor de físico (0 a 100): "))
            if 0 <= fisico <= 100:
                break
            else:
                print("Valor inválido! O físico deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o físico.")
    
    while True:
        try:
            passe = float(input("Digite o valor de passe (0 a 100): "))
            if 0 <= passe <= 100:
                break
            else:
                print("Valor inválido! O passe deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o passe.")
    
    while True:
        try:
            chute = float(input("Digite o valor de chute (0 a 100): "))
            if 0 <= chute <= 100:
                break
            else:
                print("Valor inválido! O chute deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o chute.")
    
    while True:
        try:
            defesa = float(input("Digite o valor de defesa (0 a 100): "))
            if 0 <= defesa <= 100:
                break
            else:
                print("Valor inválido! A defesa deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para a defesa.")
    
    while True:
        try:
            geral = int(input("Digite o valor geral do jogador (0 a 100): "))
            if 0 <= geral <= 100:
                break
            else:
                print("Valor inválido! O valor geral deve estar entre 0 e 100.")
        except ValueError:
            print("Por favor, insira um número válido para o valor geral.")

    # Passo 4: Inserir os atributos na tabela
    sql_atributos = """
        INSERT INTO atributos (drible, ritmo, fisico, passe, chute, defesa, geral, id_jogador)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    valores_atributos = (drible, ritmo, fisico, passe, chute, defesa, geral, jogador[0])

    # Executa o comando de inserção
    cursor.execute(sql_atributos, valores_atributos)
    print(f"Atributos do jogador '{nome_jogador}' inseridos com sucesso!")'''

def inserir_estilo_de_jogo(cursor):
    """Função para associar um estilo de jogo a um jogador"""

    # Passo 1: Solicitar o nome do estilo de jogo
    while True:
        nome_estilo = input("Digite o nome do estilo de jogo: ").title()

        # Verificar se o estilo já existe
        cursor.execute("SELECT id_estilo FROM estilos_de_jogo WHERE nome = %s", (nome_estilo,))
        estilo = cursor.fetchone()

        if estilo is None:
            # Se o estilo de jogo não existir, informar ao usuário e pedir para digitar novamente
            print(f"O estilo de jogo '{nome_estilo}' não existe. Por favor, digite um estilo válido.")
        else:
            # Caso o estilo exista, sair do loop
            print(f"O estilo de jogo '{nome_estilo}' encontrado.")
            break

    # Passo 2: Solicitar o nome do jogador
    while True:
        nome_jogador = input("Digite o nome do jogador: ").title()

        # Verificar se o jogador existe
        cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
        jogador = cursor.fetchone()

        if jogador is None:
            print(f"O jogador '{nome_jogador}' não existe no banco de dados. Vamos adicioná-lo.")
            inserir_jogador(cursor)  

            cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
            jogador = cursor.fetchone()

            if jogador is None:
                print("Erro: Jogador não foi inserido corretamente.")
                return  
            else:
                break  
        else:
            print(f"O jogador '{nome_jogador}' encontrado.")
            break

    sql_associacao = """
        INSERT INTO estilos_de_jogo_jogadores (id_estilo, id_jogador)
        VALUES (%s, %s)
    """
    
    valores_associacao = (estilo[0], jogador[0])

    cursor.execute(sql_associacao, valores_associacao)
    print(f"Estilo de jogo '{nome_estilo}' associado com sucesso ao jogador '{nome_jogador}'!")

def inserir_funcionario(cursor, conexao):
    """Insere um funcionário na tabela 'funcionarios'."""
    # Entrada de dados do funcionário
    nome_funcionario = input("Digite o nome do funcionário: ").title()
    qualidade = float(input("Digite a qualidade do funcionário (0.00 a 5.00): "))

    # Inserir ou validar o cargo
    cargo_nome = input("Digite o nome do cargo do funcionário: ").title()
    cursor.execute("SELECT id_cargo FROM cargos WHERE descricao = %s", (cargo_nome,))
    cargo = cursor.fetchone()

    if not cargo:
        print(f"O cargo '{cargo_nome}' não existe. Criando novo cargo...")
        cursor.execute("INSERT INTO cargos (descricao) VALUES (%s)", (cargo_nome,))
        conexao.commit()
        id_cargo = cursor.lastrowid
    else:
        id_cargo = cargo[0]

    # Escolher a associação esportiva pelo nome
    associacao_nome = input("Digite o nome da associação esportiva: ").title()
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s", (associacao_nome,))
    associacao = cursor.fetchone()
    if not associacao:
        print(f"Erro: Associação esportiva '{associacao_nome}' não encontrada.")
        return
    id_associacao = associacao[0]

    # Escolher a nacionalidade pelo nome (seleção)
    nacionalidade_nome = input("Digite o nome da seleção (nacionalidade): ").title()
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (nacionalidade_nome,))
    nacionalidade = cursor.fetchone()
    if not nacionalidade:
        print(f"Erro: Seleção '{nacionalidade_nome}' não encontrada.")
        return
    id_nacionalidade = nacionalidade[0]

    # Inserir funcionário
    sql_funcionario = """
        INSERT INTO funcionarios (nome, qualidade, id_associacao, id_cargo, id_nacionalidade)
        VALUES (%s, %s, %s, %s, %s)
    """
    valores = (nome_funcionario, qualidade, id_associacao, id_cargo, id_nacionalidade)
    cursor.execute(sql_funcionario, valores)
    conexao.commit()

    print(f"Funcionário '{nome_funcionario}' inserido com sucesso!")

def inserir_estatisticas(cursor, conexao):
    """Insere ou atualiza estatísticas de um jogador em um campeonato."""
    # Entrada de dados básicos
    jogador_nome = input("Digite o nome do jogador: ").title()
    campeonato_nome = input("Digite o nome do campeonato: ").title()

    # Verificar se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (jogador_nome,))
    jogador = cursor.fetchone()
    if not jogador:
        print(f"Erro: Jogador '{jogador_nome}' não encontrado.")
        return
    id_jogador = jogador[0]

    # Verificar se o campeonato existe
    cursor.execute("SELECT id_campeonato FROM campeonatos WHERE nome = %s", (campeonato_nome,))
    campeonato = cursor.fetchone()
    if not campeonato:
        print(f"Erro: Campeonato '{campeonato_nome}' não encontrado.")
        return
    id_campeonato = campeonato[0]

    # Verificar se já existem estatísticas para o jogador neste campeonato
    cursor.execute("""
        SELECT id_estatistica, gol, assist, nota_jogo, cartao_ver, cartao_ama, numero_jogos
        FROM estatisticas
        WHERE id_jogador = %s AND id_campeonato = %s
    """, (id_jogador, id_campeonato))
    estatisticas = cursor.fetchone()

    # Entrada de novos valores ou atualização dos existentes
    if estatisticas:
        print("\nEstatísticas atuais:")
        print(f"Gols: {estatisticas[1]}, Assistências: {estatisticas[2]}, Nota Média: {estatisticas[3]}, "
              f"Cartões Vermelhos: {estatisticas[4]}, Cartões Amarelos: {estatisticas[5]}, Jogos: {estatisticas[6]}")

        print("\nAtualize as estatísticas (deixe em branco para manter os valores atuais):")
        gols = input("Digite o número de gols: ").strip()
        assistencias = input("Digite o número de assistências: ").strip()
        nota_jogo = input("Digite a nota média: ").strip()
        cartoes_ver = input("Digite o número de cartões vermelhos: ").strip()
        cartoes_ama = input("Digite o número de cartões amarelos: ").strip()
        numero_jogos = input("Digite o número de jogos: ").strip()

        # Usar valores antigos se a entrada for vazia
        novos_valores = {
            "gol": int(gols) if gols else estatisticas[1],
            "assist": int(assistencias) if assistencias else estatisticas[2],
            "nota_jogo": float(nota_jogo) if nota_jogo else estatisticas[3],
            "cartao_ver": int(cartoes_ver) if cartoes_ver else estatisticas[4],
            "cartao_ama": int(cartoes_ama) if cartoes_ama else estatisticas[5],
            "numero_jogos": int(numero_jogos) if numero_jogos else estatisticas[6],
        }

        # Atualizar as estatísticas no banco
        sql_update = """
            UPDATE estatisticas
            SET gol = %s, assist = %s, nota_jogo = %s, cartao_ver = %s, cartao_ama = %s, numero_jogos = %s
            WHERE id_estatistica = %s
        """
        cursor.execute(sql_update, (
            novos_valores["gol"], novos_valores["assist"], novos_valores["nota_jogo"],
            novos_valores["cartao_ver"], novos_valores["cartao_ama"], novos_valores["numero_jogos"],
            estatisticas[0]
        ))
        conexao.commit()
        print("Estatísticas atualizadas com sucesso!")

    else:
        # Inserir novas estatísticas
        print("\nInserindo novas estatísticas.")
        gols = int(input("Digite o número de gols: "))
        assistencias = int(input("Digite o número de assistências: "))
        nota_jogo = float(input("Digite a nota média (0.00 a 10.00): "))
        cartoes_ver = int(input("Digite o número de cartões vermelhos: "))
        cartoes_ama = int(input("Digite o número de cartões amarelos: "))
        numero_jogos = int(input("Digite o número de jogos: "))

        sql_insert = """
            INSERT INTO estatisticas (gol, assist, nota_jogo, cartao_ver, cartao_ama, id_jogador, id_campeonato, numero_jogos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (gols, assistencias, nota_jogo, cartoes_ver, cartoes_ama, id_jogador, id_campeonato, numero_jogos))
        conexao.commit()
        print("Estatísticas inseridas com sucesso!")

#Funções Alterar

def alterar_clube(cursor, conexao):
    """Altera dados de um clube."""
    nome_clube = input("Digite o nome do clube que deseja alterar: ").title()

    # Verifica se o clube existe
    cursor.execute("SELECT * FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (nome_clube,))
    clube = cursor.fetchone()

    if not clube:
        print(f"O clube '{nome_clube}' não existe.")
        return

    print("Deixe em branco para manter o valor atual.")
    novo_nome = input(f"Novo nome ({clube[4]}): ").title() or clube[4]
    nova_sigla = input(f"Nova sigla ({clube[1]}): ").upper() or clube[1]
    novo_apelido = input(f"Novo apelido ({clube[2]}): ").title() or clube[2]
    nova_qualidade = input(f"Nova qualidade ({clube[3]}): ") or clube[3]
    nova_mascote = input(f"Nova mascote ({clube[5]}): ").title() or clube[5]

    # Obtém os dados do clube
    cursor.execute("""
        SELECT c.id_associacao, c.receita_em_mi, c.id_cidade, c.pais 
        FROM clubes c
        JOIN associacoes_esportivas a ON a.id_associacao = c.id_associacao
        WHERE a.nome = %s
    """, (novo_nome,))
    clube_info = cursor.fetchone()

    if not clube_info:
        print(f"Não foram encontrados detalhes do clube '{nome_clube}'.")
        return

    id_clube, receita_atual, id_cidade_atual, pais_atual = clube_info

    # Atualizar os dados do clube
    nova_receita = input(f"Nova receita em milhões ({receita_atual}): ") or receita_atual
    cidade_nome = input("Digite o nome da cidade onde o clube está localizado: ").title()

    # Verifica se o campo cidade foi deixado vazio
    if cidade_nome:
        id_cidade_inserida = inserir_cidade(cursor, cidade_nome, conexao)
    else:
        id_cidade_inserida = id_cidade_atual  # Mantém a cidade atual

    novo_pais = input(f"Novo país ({pais_atual}): ").title() or pais_atual

    # Atualiza os dados da associação
    sql_update_associacao = """
        UPDATE associacoes_esportivas
        SET nome = %s, sigla = %s, apelido = %s, qualidade = %s, mascote = %s
        WHERE id_associacao = %s
    """
    valores_associacao = (novo_nome, nova_sigla, novo_apelido, nova_qualidade, nova_mascote, clube[0])
    cursor.execute(sql_update_associacao, valores_associacao)

    sql_update_clube = """
        UPDATE clubes
        SET receita_em_mi = %s, id_cidade = %s, pais = %s
        WHERE id_associacao = %s
    """
    valores_clube = (nova_receita, id_cidade_inserida, novo_pais, id_clube)
    cursor.execute(sql_update_clube, valores_clube)

    conexao.commit()
    print(f"Clube '{nome_clube}' atualizado com sucesso!")

def alterar_selecao(cursor, conexao):
    """Altera dados de uma seleção esportiva."""
    nome_selecao = input("Digite o nome da seleção que deseja alterar: ").title()

    # Verifica se a seleção existe
    cursor.execute("SELECT * FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (nome_selecao,))
    selecao = cursor.fetchone()

    if not selecao:
        print(f"A seleção '{nome_selecao}' não existe.")
        return

    print("Deixe em branco para manter o valor atual.")
    novo_nome = input(f"Novo nome ({selecao[4]}): ").title() or selecao[4]
    nova_sigla = input(f"Nova sigla ({selecao[1]}): ").upper() or selecao[1]
    novo_apelido = input(f"Novo apelido ({selecao[2]}): ").title() or selecao[2]
    nova_qualidade = input(f"Nova qualidade ({selecao[3]}): ") or selecao[3]
    nova_mascote = input(f"Nova mascote ({selecao[5]}): ").title() or selecao[5]

    # Atualiza os dados da seleção
    sql_update = """
        UPDATE associacoes_esportivas
        SET nome = %s, sigla = %s, apelido = %s, qualidade = %s, mascote = %s
        WHERE id_associacao = %s
    """
    valores = (novo_nome, nova_sigla, novo_apelido, nova_qualidade, nova_mascote, selecao[0])
    cursor.execute(sql_update, valores)
    conexao.commit()
    print(f"Seleção '{nome_selecao}' atualizada com sucesso!")

def alterar_jogador(cursor, conexao):
    """Função para alterar dados de um jogador"""
    nome_jogador = input("Digite o nome do jogador que deseja alterar: ").title()

    # Verifica se o jogador existe no banco de dados
    cursor.execute("""
        SELECT j.id_jogador, j.nome, j.posicao, j.id_selecao, a.nome AS selecao_nome
        FROM jogadores j
        JOIN associacoes_esportivas a ON j.id_selecao = a.id_associacao
        WHERE j.nome = %s
    """, (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não foi encontrado.")
        return

    id_jogador, nome_atual, posicao_atual, id_selecao_atual, selecao_nome_atual = jogador

    print("\n--- Alterando dados do jogador ---")
    print("Deixe em branco para manter o valor atual.")
    novo_nome = input(f"Novo nome do jogador ({nome_atual}): ").title() or nome_atual

    # Alterar posição do jogador
    posicoes_validas = ["GOL", "ZAG", "LE", "LD", "ADE", "ADD", "VOL", "MC", "ME", "MD", "MEI", "PD", "PE", "SA", "ATA"]
    while True:
        nova_posicao = input(f"Nova posição do jogador ({posicao_atual}): ").upper()
        if not nova_posicao:  # Mantém a posição atual
            nova_posicao = posicao_atual
            break
        elif nova_posicao in posicoes_validas:
            break
        else:
            print("Posição inválida! Por favor, escolha uma posição válida.")

    # Alterar seleção do jogador
    nova_selecao_nome = input(f"Nova seleção do jogador ({selecao_nome_atual}): ").title() or selecao_nome_atual

    # Verifica se a nova seleção existe
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (nova_selecao_nome,))
    nova_selecao = cursor.fetchone()

    if not nova_selecao:
        print(f"A seleção '{nova_selecao_nome}' não existe no banco de dados. Vamos adicioná-la.")
        id_selecao_nova = inserir_associacao(cursor, tipo="selecao")
        inserir_selecao(cursor, id_selecao_nova)
    else:
        id_selecao_nova = nova_selecao[0]

    # Atualiza os dados do jogador no banco
    sql_update = """
        UPDATE jogadores
        SET nome = %s, posicao = %s, id_selecao = %s
        WHERE id_jogador = %s
    """
    valores = (novo_nome, nova_posicao, id_selecao_nova, id_jogador)
    cursor.execute(sql_update, valores)
    conexao.commit()

    print(f"Jogador '{nome_jogador}' atualizado com sucesso!")

def alterar_estadio(cursor, conexao):
    """Função para alterar os dados de um estádio associado a um clube"""
    
    # Perguntar o nome do clube e do estádio
    nome_clube = input("Digite o nome do clube ao qual o estádio está atrelado: ").title()
    nome_estadio = input("Digite o nome do estádio que deseja alterar: ").title()

    # Verificar se o estádio existe
    cursor.execute("""
        SELECT e.id_estadio, e.nome, e.capacidade
        FROM estadios e
        JOIN clube_estadios ce ON e.id_estadio = ce.id_estadio
        JOIN associacoes_esportivas a ON ce.id_associacao = a.id_associacao
        WHERE e.nome = %s AND a.nome = %s
    """, (nome_estadio, nome_clube))
    estadio = cursor.fetchone()

    if not estadio:
        print(f"O estádio '{nome_estadio}' não está associado ao clube '{nome_clube}'.")
        print("Vamos criar o estádio primeiro.")
        
        # Se o estádio não existir, criá-lo
        inserir_estadio(cursor, nome_estadio)

        # Após criar o estádio, buscar novamente para pegar os dados completos
        cursor.execute("SELECT id_estadio, nome, capacidade FROM estadios WHERE nome = %s", (nome_estadio,))
        estadio = cursor.fetchone()

        if not estadio:
            print(f"Erro ao criar o estádio '{nome_estadio}'.")
            return

    # Garantir que estamos desempacotando apenas 3 valores: id_estadio, nome, e capacidade
    id_estadio, nome_atual, capacidade_atual = estadio

    # Alterar dados do estádio
    print("\n--- Alterando dados do estádio ---")
    print("Deixe em branco para manter o valor atual.")
    novo_nome_estadio = input(f"Novo nome do estádio ({nome_atual}): ").title() or nome_atual
    while True:
        try:
            nova_capacidade = input(f"Nova capacidade do estádio ({capacidade_atual}): ")
            if not nova_capacidade:  # Mantém o valor atual se vazio
                nova_capacidade = capacidade_atual
                break
            nova_capacidade = int(nova_capacidade)
            if 1000 <= nova_capacidade <= 100000:
                break
            else:
                print("Capacidade inválida! Deve estar entre 1000 e 100000.")
        except ValueError:
            print("Por favor, insira um número válido para a capacidade.")

    # Atualiza os dados do estádio
    sql_update_estadio = """
        UPDATE estadios
        SET nome = %s, capacidade = %s
        WHERE id_estadio = %s
    """
    valores_estadio = (novo_nome_estadio, nova_capacidade, id_estadio)
    cursor.execute(sql_update_estadio, valores_estadio)
    conexao.commit()
    print(f"Estádio '{nome_atual}' atualizado para '{novo_nome_estadio}' com sucesso!\n")

    # Alterar associação do estádio
    print("--- Alterando associação do estádio ---")
    novo_nome_clube = input(f"Novo clube para o estádio ({nome_clube}): ").title() or nome_clube

    # Verifica se o clube existe
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (novo_nome_clube,))
    novo_clube = cursor.fetchone()

    if not novo_clube:
        print(f"O clube '{novo_nome_clube}' não existe. Vamos criá-lo.")
        id_nova_associacao = inserir_associacao(cursor, tipo="clube")
        inserir_clube(cursor, id_nova_associacao, conexao)
    else:
        id_nova_associacao = novo_clube[0]

    # Atualizar a associação do estádio na tabela `clube_estadios`
    sql_update_associacao = """
        UPDATE clube_estadios
        SET id_associacao = %s
        WHERE id_estadio = %s
    """
    valores_associacao = (id_nova_associacao, id_estadio)
    cursor.execute(sql_update_associacao, valores_associacao)
    conexao.commit()
    print(f"Estádio '{novo_nome_estadio}' agora está associado ao clube '{novo_nome_clube}' com sucesso!")

def alterar_contrato(cursor, conexao):
    """Função para alterar o contrato de um jogador com um clube"""
    nome_jogador = input("Digite o nome do jogador cujo contrato você deseja alterar: ").title()

    # Verificar se o jogador existe e buscar o contrato
    cursor.execute("""
        SELECT j.id_jogador, c.numero, c.id_associacao
        FROM jogadores j
        JOIN contratos c ON j.id_jogador = c.id_jogador
        WHERE j.nome = %s
    """, (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não foi encontrado ou não possui contrato registrado.")
        return

    id_jogador, numero_atual, id_clube = jogador

    # Buscar o contrato atual do jogador
    cursor.execute("""
        SELECT id_contrato, salario, data_inicial, duracao, bonus, luvas, multarecisoria
        FROM contratos
        WHERE id_jogador = %s AND id_associacao = %s
    """, (id_jogador, id_clube))

    contrato = cursor.fetchone()

    if not contrato:
        print(f"O contrato do jogador '{nome_jogador}' não foi encontrado.")
        return

    id_contrato, salario_atual, data_inicial_atual, duracao_atual, bonus_atual, luvas_atual, multa_recisoria_atual = contrato

    print("\n--- Alterando dados do contrato ---")
    print("Deixe em branco para manter o valor atual.")
    
    # Atualizar o número do jogador
    novo_numero = input(f"Novo número do jogador (atualmente {numero_atual}): ")
    novo_numero = int(novo_numero) if novo_numero else numero_atual

    # Atualizar salário
    novo_salario = input(f"Novo salário do jogador (atualmente {salario_atual}): ")
    novo_salario = float(novo_salario) if novo_salario else salario_atual

    # Atualizar data de início
    nova_data_inicial = input(f"Nova data de início do contrato (atualmente {data_inicial_atual}): ")
    nova_data_inicial = nova_data_inicial if nova_data_inicial else data_inicial_atual

    # Atualizar data de término
    nova_duracao = input(f"Nova data de término do contrato (atualmente {duracao_atual}): ")
    nova_duracao = nova_duracao if nova_duracao else duracao_atual

    # Atualizar bônus
    novo_bonus = input(f"Novo bônus (atualmente {bonus_atual}): ")
    novo_bonus = float(novo_bonus) if novo_bonus else bonus_atual

    # Atualizar luvas
    novo_luvas = input(f"Novo valor das luvas (atualmente {luvas_atual}): ")
    novo_luvas = float(novo_luvas) if novo_luvas else luvas_atual

    # Atualizar multa recisória
    nova_multa_recisoria = input(f"Novo valor da multa recisória (atualmente {multa_recisoria_atual}): ")
    nova_multa_recisoria = float(nova_multa_recisoria) if nova_multa_recisoria else multa_recisoria_atual

    # Atualizar os dados do contrato no banco de dados
    sql_update_contrato = """
        UPDATE contratos
        SET salario = %s, data_inicial = %s, duracao = %s, bonus = %s, luvas = %s, multarecisoria = %s
        WHERE id_contrato = %s
    """
    valores_contrato = (novo_salario, nova_data_inicial, nova_duracao, novo_bonus, novo_luvas, nova_multa_recisoria, id_contrato)
    cursor.execute(sql_update_contrato, valores_contrato)

    # Atualizar o número do jogador
    sql_update_numero = """
        UPDATE contratos
        SET numero = %s
        WHERE id_jogador = %s AND id_associacao = %s
    """
    cursor.execute(sql_update_numero, (novo_numero, id_jogador, id_clube))

    conexao.commit()

    print(f"Contrato do jogador '{nome_jogador}' atualizado com sucesso!")

'''
def alterar_atributos(cursor, conexao):
    """Função para alterar os atributos de um jogador"""
    
    # Passo 1: Solicitar o nome do jogador
    nome_jogador = input("Digite o nome do jogador cujo atributo você deseja alterar: ").title()

    # Passo 2: Verificar se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if jogador is None:
        print(f"O jogador '{nome_jogador}' não existe no banco de dados.")
        return  # Sai da função caso o jogador não exista

    # Passo 3: Verificar se o jogador já tem atributos registrados
    cursor.execute("SELECT * FROM atributos WHERE id_jogador = %s", (jogador[0],))
    atributos = cursor.fetchone()

    if atributos is None:
        print(f"O jogador '{nome_jogador}' não possui atributos registrados.")
        return  # Sai da função caso o jogador não tenha atributos registrados

    # Passo 4: Coletar os novos valores dos atributos (se desejado)
    print("\n--- Alterando atributos do jogador ---")
    print("Deixe em branco para manter o valor atual.")
    
    # Atualizar drible
    novo_drible = input(f"Novo valor de drible (atualmente {atributos[1]}): ")
    novo_drible = float(novo_drible) if novo_drible else atributos[1]

    # Atualizar ritmo
    novo_ritmo = input(f"Novo valor de ritmo (atualmente {atributos[2]}): ")
    novo_ritmo = float(novo_ritmo) if novo_ritmo else atributos[2]

    # Atualizar físico
    novo_fisico = input(f"Novo valor de físico (atualmente {atributos[3]}): ")
    novo_fisico = float(novo_fisico) if novo_fisico else atributos[3]

    # Atualizar passe
    novo_passe = input(f"Novo valor de passe (atualmente {atributos[4]}): ")
    novo_passe = float(novo_passe) if novo_passe else atributos[4]

    # Atualizar chute
    novo_chute = input(f"Novo valor de chute (atualmente {atributos[5]}): ")
    novo_chute = float(novo_chute) if novo_chute else atributos[5]

    # Atualizar defesa
    nova_defesa = input(f"Novo valor de defesa (atualmente {atributos[6]}): ")
    nova_defesa = float(nova_defesa) if nova_defesa else atributos[6]

    # Atualizar geral
    novo_geral = input(f"Novo valor geral (atualmente {atributos[7]}): ")
    novo_geral = int(novo_geral) if novo_geral else atributos[7]

    # Passo 5: Atualizar os atributos no banco de dados
    sql_update_atributos = """
        UPDATE atributos
        SET drible = %s, ritmo = %s, fisico = %s, passe = %s, chute = %s, defesa = %s, geral = %s
        WHERE id_jogador = %s
    """
    
    valores_atributos = (novo_drible, novo_ritmo, novo_fisico, novo_passe, novo_chute, nova_defesa, novo_geral, jogador[0])

    # Executa o comando de atualização
    cursor.execute(sql_update_atributos, valores_atributos)
    conexao.commit()
    
    print(f"Atributos do jogador '{nome_jogador}' atualizados com sucesso!")'''

def alterar_estilo_de_jogo(cursor, conexao):
    """Função para alterar o estilo de jogo de um jogador"""
    
    # Passo 1: Solicitar o nome do jogador
    nome_jogador = input("Digite o nome do jogador cujo estilo de jogo você deseja alterar: ").title()

    # Verificar se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não foi encontrado no banco de dados.")
        return  # Sai da função caso o jogador não exista

    id_jogador = jogador[0]

    # Passo 2: Verificar os estilos de jogo atuais do jogador
    cursor.execute("""
        SELECT e.id_estilo, e.nome
        FROM estilos_de_jogo e
        JOIN estilos_de_jogo_jogadores ej ON e.id_estilo = ej.id_estilo
        WHERE ej.id_jogador = %s
    """, (id_jogador,))
    estilos_atual = cursor.fetchall()

    if not estilos_atual:
        print(f"O jogador '{nome_jogador}' não tem estilos de jogo associados.")
        return  # Sai da função caso o jogador não tenha estilos de jogo

    # Exibir todos os estilos de jogo associados ao jogador
    print(f"Estilos de jogo atuais do jogador '{nome_jogador}':")
    for idx, estilo in enumerate(estilos_atual, 1):
        print(f"{idx}. {estilo[1]}")  # Mostra o nome do estilo

    # Passo 3: Solicitar ao usuário qual estilo deseja alterar
    while True:
        try:
            escolha = int(input(f"\nEscolha o número do estilo de jogo que deseja alterar (1-{len(estilos_atual)}): "))
            if 1 <= escolha <= len(estilos_atual):
                estilo_selecionado = estilos_atual[escolha - 1]
                print(f"Você escolheu o estilo de jogo '{estilo_selecionado[1]}'.")
                break
            else:
                print(f"Por favor, escolha um número entre 1 e {len(estilos_atual)}.")
        except ValueError:
            print("Por favor, insira um número válido.")

    # Passo 4: Solicitar o nome do novo estilo de jogo
    while True:
        nome_estilo = input("Digite o nome do novo estilo de jogo: ").title()

        # Verificar se o estilo já existe
        cursor.execute("SELECT id_estilo FROM estilos_de_jogo WHERE nome = %s", (nome_estilo,))
        estilo = cursor.fetchone()

        if estilo is None:
            print(f"O estilo de jogo '{nome_estilo}' não existe. Tente novamente.")
        else:
            print(f"O estilo de jogo '{nome_estilo}' encontrado.")
            break

    # Passo 5: Atualizar o estilo de jogo no banco de dados
    # Remover o estilo de jogo atual e associar o novo
    cursor.execute("""
        DELETE FROM estilos_de_jogo_jogadores WHERE id_jogador = %s AND id_estilo = %s
    """, (id_jogador, estilo_selecionado[0]))  # Remove o estilo atual
    print(f"Estilo de jogo '{estilo_selecionado[1]}' removido do jogador '{nome_jogador}'.")

    # Associar o novo estilo de jogo ao jogador
    sql_associacao = """
        INSERT INTO estilos_de_jogo_jogadores (id_estilo, id_jogador)
        VALUES (%s, %s)
    """
    valores_associacao = (estilo[0], id_jogador)

    cursor.execute(sql_associacao, valores_associacao)
    conexao.commit()  # Confirma a alteração no banco de dados

    print(f"Estilo de jogo '{nome_estilo}' associado com sucesso ao jogador '{nome_jogador}'!")

def alterar_funcionario(cursor, conexao):
    """Altera dados de um funcionário na tabela 'funcionarios'."""
    nome_funcionario = input("Digite o nome do funcionário que deseja alterar: ").title()
    # Verifica se o funcionário existe
    cursor.execute("SELECT * FROM funcionarios WHERE nome = %s", (nome_funcionario,))
    funcionario = cursor.fetchone()

    if not funcionario:
        print(f"O funcionário '{nome_funcionario}' não existe.")
        return

    print("Deixe em branco para manter o valor atual.")
    novo_nome = input(f"Novo nome ({funcionario[1]}): ").title() or funcionario[1]
    nova_qualidade = input(f"Nova qualidade ({funcionario[2]}): ") or funcionario[2]

    # Atualiza o cargo
    cargo_atual = input("Digite o cargo atual do funcionário: ").title()
    cursor.execute("SELECT id_cargo FROM cargos WHERE descricao = %s", (cargo_atual,))
    cargo = cursor.fetchone()

    if not cargo:
        print(f"Cargo '{cargo_atual}' não encontrado.")
        return

    id_cargo = cargo[0]

    # Atualiza a nacionalidade
    nova_nacionalidade = input("Digite a nova seleção (nacionalidade): ").title()
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (nova_nacionalidade,))
    nacionalidade = cursor.fetchone()

    if not nacionalidade:
        print(f"Seleção '{nova_nacionalidade}' não encontrada.")
        return

    id_nacionalidade = nacionalidade[0]

    # Atualiza os dados no banco
    sql_update = """
        UPDATE funcionarios
        SET nome = %s, qualidade = %s, id_cargo = %s, id_nacionalidade = %s
        WHERE id_funcionario = %s
    """
    valores = (novo_nome, nova_qualidade, id_cargo, id_nacionalidade, funcionario[0])
    cursor.execute(sql_update, valores)
    conexao.commit()
    print(f"Funcionário '{nome_funcionario}' atualizado com sucesso!")

def alterar_campeonato(cursor, conexao):
    """Altera dados de um campeonato na tabela 'campeonatos'."""
    nome_campeonato = input("Digite o nome do campeonato que deseja alterar: ").title()

    # Verifica se o campeonato existe
    cursor.execute("SELECT * FROM campeonatos WHERE nome = %s", (nome_campeonato,))
    campeonato = cursor.fetchone()

    if not campeonato:
        print(f"O campeonato '{nome_campeonato}' não existe.")
        return

    print("Deixe em branco para manter o valor atual.")
    novo_nome = input(f"Novo nome do campeonato ({campeonato[1]}): ").title() or campeonato[1]

    # Atualiza os dados no banco
    sql_update = "UPDATE campeonatos SET nome = %s WHERE id_campeonato = %s"
    cursor.execute(sql_update, (novo_nome, campeonato[0]))
    conexao.commit()
    print(f"Campeonato '{nome_campeonato}' atualizado com sucesso!")

#Funções excluir

def excluir_campeonato(cursor, conexao):
    """Exclui um campeonato da tabela 'campeonatos'."""
    nome_campeonato = input("Digite o nome do campeonato que deseja excluir: ").title()

    # Verifica se o campeonato existe
    cursor.execute("SELECT id_campeonato FROM campeonatos WHERE nome = %s", (nome_campeonato,))
    campeonato = cursor.fetchone()

    if not campeonato:
        print(f"O campeonato '{nome_campeonato}' não existe.")
        return

    # Exclui o campeonato
    sql_delete = "DELETE FROM campeonatos WHERE id_campeonato = %s"
    cursor.execute(sql_delete, (campeonato[0],))
    conexao.commit()
    print(f"Campeonato '{nome_campeonato}' excluído com sucesso!")

def excluir_funcionario(cursor, conexao):
    """Exclui um funcionário da tabela 'funcionarios'."""
    nome_funcionario = input("Digite o nome do funcionário que deseja excluir: ").title()

    # Verifica se o funcionário existe
    cursor.execute("SELECT id_funcionario FROM funcionarios WHERE nome = %s", (nome_funcionario,))
    funcionario = cursor.fetchone()

    if not funcionario:
        print(f"O funcionário '{nome_funcionario}' não existe.")
        return

    # Exclui o funcionário
    sql_delete = "DELETE FROM funcionarios WHERE id_funcionario = %s"
    cursor.execute(sql_delete, (funcionario[0],))
    conexao.commit()
    print(f"Funcionário '{nome_funcionario}' excluído com sucesso!")

def excluir_contrato(cursor, conexao):
    """Exclui um contrato de um jogador."""
    nome_jogador = input("Digite o nome do jogador cujo contrato deseja excluir: ").title()

    # Verifica se o contrato existe
    cursor.execute("""
        SELECT c.id_contrato
        FROM contratos c
        JOIN jogadores j ON c.id_jogador = j.id_jogador
        WHERE j.nome = %s
    """, (nome_jogador,))
    contrato = cursor.fetchone()

    if not contrato:
        print(f"Contrato do jogador '{nome_jogador}' não encontrado.")
        return

    # Exclui o contrato
    sql_delete = "DELETE FROM contratos WHERE id_contrato = %s"
    cursor.execute(sql_delete, (contrato[0],))
    conexao.commit()
    print(f"Contrato do jogador '{nome_jogador}' excluído com sucesso!")

def excluir_atributos(cursor, conexao):
    """Exclui os atributos de um jogador."""
    nome_jogador = input("Digite o nome do jogador cujos atributos deseja excluir: ").title()

    # Verifica se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não existe.")
        return

    # Exclui os atributos
    sql_delete = "DELETE FROM atributos WHERE id_jogador = %s"
    cursor.execute(sql_delete, (jogador[0],))
    conexao.commit()
    print(f"Atributos do jogador '{nome_jogador}' excluídos com sucesso!")

def excluir_estilo_de_jogo(cursor, conexao):
    """Exclui estilos de jogo associados a um jogador."""
    nome_jogador = input("Digite o nome do jogador cujo estilo de jogo deseja excluir: ").title()

    # Verifica se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não existe.")
        return

    # Exclui os estilos de jogo associados
    sql_delete = "DELETE FROM estilos_de_jogo_jogadores WHERE id_jogador = %s"
    cursor.execute(sql_delete, (jogador[0],))
    conexao.commit()
    print(f"Estilos de jogo do jogador '{nome_jogador}' excluídos com sucesso!")

def excluir_jogador(cursor, conexao):
    """Exclui um jogador da tabela 'jogadores'."""
    nome_jogador = input("Digite o nome do jogador que deseja excluir: ").title()

    # Verifica se o jogador existe
    cursor.execute("SELECT id_jogador FROM jogadores WHERE nome = %s", (nome_jogador,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"O jogador '{nome_jogador}' não existe.")
        return

    # Exclui o jogador
    sql_delete = "DELETE FROM jogadores WHERE id_jogador = %s"
    cursor.execute(sql_delete, (jogador[0],))
    conexao.commit()
    print(f"Jogador '{nome_jogador}' excluído com sucesso!")

def excluir_clube(cursor, conexao):
    """Exclui um clube da tabela 'associacoes_esportivas' e tabelas relacionadas."""
    nome_clube = input("Digite o nome do clube que deseja excluir: ").title()

    # Verifica se o clube existe
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'clube'", (nome_clube,))
    clube = cursor.fetchone()

    if not clube:
        print(f"O clube '{nome_clube}' não existe.")
        return

    # Exclui o clube
    sql_delete = "DELETE FROM associacoes_esportivas WHERE id_associacao = %s"
    cursor.execute(sql_delete, (clube[0],))
    conexao.commit()
    print(f"Clube '{nome_clube}' excluído com sucesso!")

def excluir_selecao(cursor, conexao):
    """Exclui uma seleção e move os jogadores para a seleção 'Passe Livre'."""
    nome_selecao = input("Digite o nome da seleção que deseja excluir: ").title()

    # Verifica se a seleção existe
    cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = %s AND tipo = 'selecao'", (nome_selecao,))
    selecao = cursor.fetchone()

    if not selecao:
        print(f"A seleção '{nome_selecao}' não existe.")
        return

    # Verifica se existem jogadores atrelados à seleção
    cursor.execute("SELECT id_jogador FROM jogadores WHERE id_selecao = %s", (selecao[0],))
    jogadores = cursor.fetchall()

    if jogadores:
        # Se houver jogadores, verifica se a seleção "Passe Livre" existe
        cursor.execute("SELECT id_associacao FROM associacoes_esportivas WHERE nome = 'Passe Livre' AND tipo = 'selecao'")
        passe_livre = cursor.fetchone()

        if not passe_livre:
            print("Erro: A seleção 'Passe Livre' não existe. Verifique os dados no banco de dados.")
            return

        # Atualiza os jogadores para a seleção "Passe Livre"
        cursor.execute("UPDATE jogadores SET id_selecao = %s WHERE id_selecao = %s", (passe_livre[0], selecao[0]))
        conexao.commit()
        print(f"Jogadores da seleção '{nome_selecao}' foram transferidos para 'Passe Livre'.")
    # Exclui a seleção
    cursor.execute("DELETE FROM associacoes_esportivas WHERE id_associacao = %s", (selecao[0],))
    conexao.commit()
    print(f"Seleção '{nome_selecao}' excluída com sucesso!")

#funcao para select

def mostrar_clubes(cursor):
    """Mostra todos os clubes existentes com exibição formatada."""
    try:
        cursor.execute("SELECT nome, sigla, apelido, formacao FROM associacoes_esportivas WHERE tipo = 'clube'")
        clubes = cursor.fetchall()

        if not clubes:
            print("Nenhum clube encontrado.")
        else:
            print("\n--- Clubes Existentes ---")
            # Criação da tabela com tabulate
            tabela = tabulate(clubes, headers=["Nome", "Sigla", "Apelido", "Formacao"], tablefmt="grid")
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar clubes: {e}")

def mostrar_selecoes(cursor):
    """Mostra todas as seleções existentes com exibição formatada."""
    try:
        cursor.execute("SELECT nome, sigla, apelido, formacao FROM associacoes_esportivas WHERE tipo = 'selecao'")
        selecoes = cursor.fetchall()

        if not selecoes:
            print("Nenhuma seleção encontrada.")
        else:
            print("\n--- Seleções Existentes ---")
            # Criação da tabela com tabulate
            tabela = tabulate(selecoes, headers=["Nome", "Sigla", "Apelido", "formacao"], tablefmt="grid")
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar seleções: {e}")

def mostrar_jogadores(cursor):
    """Mostra todos os jogadores existentes com exibição formatada."""
    try:
        cursor.execute("""
            SELECT j.nome, j.posicao, a.nome AS selecao
            FROM jogadores j
            LEFT JOIN associacoes_esportivas a ON j.id_selecao = a.id_associacao
        """)
        jogadores = cursor.fetchall()

        if not jogadores:
            print("Nenhum jogador encontrado.")
        else:
            print("\n--- Jogadores Existentes ---")
            # Criação da tabela com tabulate
            tabela = tabulate(jogadores, headers=["Nome", "Posição", "Seleção"], tablefmt="grid")
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar jogadores: {e}")

def mostrar_jogadores_contrato(cursor):
    """Mostra todos os jogadores que possuem contrato com algum clube."""
    try:
        cursor.execute("""
            SELECT j.nome AS jogador, c.numero AS numero_camisa, a.nome AS clube, c.salario
            FROM jogadores j
            INNER JOIN contratos c ON j.id_jogador = c.id_jogador
            INNER JOIN associacoes_esportivas a ON c.id_associacao = a.id_associacao
        """)
        jogadores_contrato = cursor.fetchall()

        if not jogadores_contrato:
            print("Nenhum jogador com contrato encontrado.")
        else:
            print("\n--- Jogadores com Contratos ---")
            # Formatação com tabulate
            tabela = tabulate(
                jogadores_contrato,
                headers=["Jogador", "Número da Camisa", "Clube", "Salário"],
                tablefmt="grid",
                floatfmt=".2f"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar jogadores e contratos: {e}")

def mostrar_jogadores_geral(cursor):
    """Mostra todos os jogadores e seus valores gerais de atributos."""
    try:
        cursor.execute("""
            SELECT j.nome, a.geral
            FROM jogadores j
            INNER JOIN atributos a ON j.id_jogador = a.id_jogador
        """)
        jogadores_geral = cursor.fetchall()

        if not jogadores_geral:
            print("Nenhum jogador com atributos encontrado.")
        else:
            print("\n--- Jogadores e seus Atributos Gerais ---")
            # Formatação com tabulate
            tabela = tabulate(
                jogadores_geral,
                headers=["Jogador", "Geral"],
                tablefmt="grid"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar jogadores e atributos: {e}")

def mostrar_jogadores_estilos(cursor):
    """Mostra todos os jogadores e seus estilos de jogo, mesmo que tenham múltiplos estilos."""
    try:
        cursor.execute("""
            SELECT j.nome AS jogador, e.nome AS estilo
            FROM jogadores j
            INNER JOIN estilos_de_jogo_jogadores ej ON j.id_jogador = ej.id_jogador
            INNER JOIN estilos_de_jogo e ON ej.id_estilo = e.id_estilo
            ORDER BY j.nome
        """)
        jogadores_estilos = cursor.fetchall()

        if not jogadores_estilos:
            print("Nenhum jogador com estilos de jogo encontrado.")
        else:
            print("\n--- Jogadores e seus Estilos de Jogo ---")
            # Preparação dos dados para exibição
            tabela = tabulate(
                jogadores_estilos,
                headers=["Jogador", "Estilo de Jogo"],
                tablefmt="grid"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar jogadores e estilos de jogo: {e}")

def mostrar_funcionarios(cursor):
    """Mostra todos os funcionários registrados no banco de dados."""
    try:
        cursor.execute("""
            SELECT f.nome AS funcionario, c.descricao AS cargo, a.nome AS associacao
            FROM funcionarios f
            INNER JOIN cargos c ON f.id_cargo = c.id_cargo
            INNER JOIN associacoes_esportivas a ON f.id_associacao = a.id_associacao
        """)
        funcionarios = cursor.fetchall()

        if not funcionarios:
            print("Nenhum funcionário encontrado.")
        else:
            print("\n--- Funcionários Registrados ---")
            # Formatação com tabulate
            tabela = tabulate(
                funcionarios,
                headers=["Funcionário", "Cargo", "Associação"],
                tablefmt="grid"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar funcionários: {e}")

def mostrar_estadios_e_clubes(cursor):
    """Mostra todos os estádios e seus respectivos clubes."""
    try:
        cursor.execute("""
            SELECT e.nome AS estadio, e.capacidade, c.nome AS clube
            FROM estadios e
            INNER JOIN clube_estadios ce ON e.id_estadio = ce.id_estadio
            INNER JOIN associacoes_esportivas c ON ce.id_associacao = c.id_associacao
        """)
        estadios_clubes = cursor.fetchall()

        if not estadios_clubes:
            print("Nenhum estádio encontrado ou associado a clubes.")
        else:
            print("\n--- Estádios e seus Clubes ---")
            # Formatação com tabulate
            tabela = tabulate(
                estadios_clubes,
                headers=["Estádio", "Capacidade", "Clube"],
                tablefmt="grid",
                numalign="right"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar estádios e clubes: {e}")

def mostrar_campeonatos(cursor):
    """Mostra todos os campeonatos registrados no banco de dados."""
    try:
        cursor.execute("""
            SELECT id_campeonato, nome
            FROM campeonatos
        """)
        campeonatos = cursor.fetchall()

        if not campeonatos:
            print("Nenhum campeonato encontrado.")
        else:
            print("\n--- Campeonatos Registrados ---")
            # Formatação com tabulate
            tabela = tabulate(
                campeonatos,
                headers=["ID", "Nome do Campeonato"],
                tablefmt="grid",
                numalign="right"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar campeonatos: {e}")

def mostrar_campeonatos_associacoes(cursor):
    """Mostra os campeonatos, associações participantes e suas classificações."""
    try:
        cursor.execute("""
            SELECT 
                c.nome AS campeonato,
                a.nome AS associacao,
                ca.classificacao
            FROM campeonatos_associacoes ca
            INNER JOIN campeonatos c ON ca.id_campeonato = c.id_campeonato
            INNER JOIN associacoes_esportivas a ON ca.id_associacao = a.id_associacao
            ORDER BY c.nome, ca.classificacao
        """)
        resultados = cursor.fetchall()

        if not resultados:
            print("Nenhum campeonato ou associação encontrada.")
        else:
            print("\n--- Campeonatos, Associações e Classificações ---")
            # Preparação dos dados para exibição
            tabela = tabulate(
                resultados,
                headers=["Campeonato", "Associação", "Classificação"],
                tablefmt="grid"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar dados: {e}")

def mostrar_estatisticas(cursor):
    """Mostra as estatísticas dos jogadores em campeonatos."""
    try:
        cursor.execute("""
            SELECT 
                j.nome AS jogador,
                ca.nome AS campeonato,
                e.gol AS gols,
                e.assist AS assistencias,
                e.nota_jogo AS nota_media,
                e.numero_jogos AS jogos
            FROM estatisticas e
            INNER JOIN jogadores j ON e.id_jogador = j.id_jogador
            INNER JOIN campeonatos ca ON e.id_campeonato = ca.id_campeonato
            ORDER BY ca.nome, j.nome
        """)
        estatisticas = cursor.fetchall()

        if not estatisticas:
            print("Nenhuma estatística encontrada.")
        else:
            print("\n--- Estatísticas dos Jogadores em Campeonatos ---")
            # Formatação com tabulate
            tabela = tabulate(
                estatisticas,
                headers=["Jogador", "Campeonato", "Gols", "Assistências", "Nota","Jogos"],
                tablefmt="grid",
                floatfmt=".2f"
            )
            print(tabela)
    except Error as e:
        print(f"Erro ao buscar estatísticas: {e}")

def menu():
    """Menu principal com categorias organizadas"""
    while True:
        print("\nMENU PRINCIPAL:")
        print("1 - Inserir")
        print("2 - Alterar")
        print("3 - Deletar")
        print("4 - Mostrar")
        print("5 - Fluxo Geral (Automatizado)")
        print("X - SAIR")

        escolha = input("Escolha uma categoria: ").strip().upper()

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                menu_inserir()
            elif escolha == "2":
                menu_alterar()
            elif escolha == "3":
                menu_excluir()
            elif escolha == "4":
                menu_select()
            elif escolha == "5":
                fluxo_geral(cursor, conexao)
            else:
                print("Saindo...")
                break

            cursor.close()
            conexao.close()

def menu_inserir():
    """Submenu para opções de inserir"""
    while True:
        print("\nMENU INSERIR:")
        print("1 - Inserir Clube")
        print("2 - Inserir Selecao")
        print("3 - Inserir Jogador")
        print("4 - Inserir Estadio")
        print("5 - Inserir Estadio a um Clube")
        print("6 - Inserir Campeonato")
        print("7 - Inserir Associacao a um Campeonato")
        print("8 - Inserir Partidas a um Campeonato")
        print("9 - Inserir Atributos")
        print("10 - Inserir Contratos")
        print("11 - Inserir Estilo de Jogo")
        print("12 - Inserir Funcionario")
        print("13 - Inserir Estatisticas")
        print("X - Voltar ao Menu Principal")

        escolha = input("Escolha uma opção: ").strip().upper()

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                id_associacao_inserido = inserir_associacao(cursor, tipo="clube")
                inserir_clube(cursor, id_associacao_inserido, conexao)
            elif escolha == "2":
                id_associacao_inserido = inserir_associacao(cursor, tipo="selecao")
                inserir_selecao(cursor, id_associacao_inserido)
            elif escolha == "3":
                inserir_jogador(cursor)
            elif escolha == "4":
                nome_estadio = input("Digite o nome do estadio: ").title()
                inserir_estadio(cursor, nome_estadio)
            elif escolha == "5":
                inserir_estadio_a_clube(cursor, conexao)
            elif escolha == "6":
                inserir_campeonato(cursor, conexao)
            elif escolha == "7":
                nome_campeonato = input("Digite o nome do campeonato: ").title()
                inserir_associacoes_campeonato(cursor, conexao, nome_campeonato)
            elif escolha == "8":
                nome_campeonato = input("Digite o nome do campeonato: ").title()
                inserir_partidas_campeonato(cursor, conexao, nome_campeonato)
            elif escolha == "9":
                inserir_atributos(cursor)
            elif escolha == "10":
                inserir_contrato(cursor)
            elif escolha == "11":
                inserir_estilo_de_jogo(cursor)
            elif escolha == "12":
                inserir_funcionario(cursor, conexao)
            elif escolha == "13":
                inserir_estatisticas(cursor, conexao)
            else:
                break

            conexao.commit()
            cursor.close()
            conexao.close()

def menu_alterar():
    """Submenu para opções de alterar"""
    while True:
        print("\nMENU ALTERAR:")
        print("1 - Alterar Clube")
        print("2 - Alterar Selecao")
        print("3 - Alterar Jogador")
        print("4 - Alterar Estadio a um Clube")
        print("5 - Alterar Contrato")
        print("6 - Alterar Atributos")
        print("7 - Alterar Estilo de Jogo")
        print("8 - Alterar Funcionario")
        print("9 - Alterar Campeonato")
        print("X - Voltar ao Menu Principal")

        escolha = input("Escolha uma opção: ").strip().upper()

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                alterar_clube(cursor, conexao)
            elif escolha == "2":
                alterar_selecao(cursor, conexao)
            elif escolha == "3":
                alterar_jogador(cursor, conexao)
            elif escolha == "4":
                alterar_estadio(cursor, conexao)
            elif escolha == "5":
                alterar_contrato(cursor, conexao)
            elif escolha == "6":
                alterar_atributos(cursor)
            elif escolha == "7":
                alterar_estilo_de_jogo(cursor, conexao)
            elif escolha == "8":
                alterar_funcionario(cursor, conexao)
            elif escolha == "9":
                alterar_campeonato(cursor, conexao)
            else:
                break

            conexao.commit()
            cursor.close()
            conexao.close()

def menu_excluir():
    """Submenu para opções de excluir"""
    while True:
        print("\nMENU EXCLUIR:")
        print("1 - Excluir Campeonato")
        print("2 - Excluir Funcionario")
        print("3 - Excluir Contrato")
        print("4 - Excluir Atributos")
        print("5 - Excluir Estilo de Jogo")
        print("6 - Excluir Jogador")
        print("7 - Excluir Clube")
        print("8 - Excluir Selecao")
        print("X - Voltar ao Menu Principal")

        escolha = input("Escolha uma opção: ").strip().upper()

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                excluir_campeonato(cursor, conexao)
            elif escolha == "2":
                excluir_funcionario(cursor, conexao)
            elif escolha == "3":
                excluir_contrato(cursor, conexao)
            elif escolha == "4":
                excluir_atributos(cursor, conexao)
            elif escolha == "5":
                excluir_estilo_de_jogo(cursor, conexao)
            elif escolha == "6":
                excluir_jogador(cursor, conexao)
            elif escolha == "7":
                excluir_clube(cursor, conexao)
            elif escolha == "8":
                excluir_selecao(cursor, conexao)
            else:
                break

            conexao.commit()
            cursor.close()
            conexao.close()

def menu_select():
    """Submenu para opções de consultar dados"""
    while True:
        print("\nMENU Select:")
        print("1 - Consultar Clubes")
        print("2 - Consultar Seleções")
        print("3 - Consultar Jogadores")
        print("4 - Consultar Jogadores com Contrato")
        print("5 - Consultar Atributos Gerais dos Jogadores")
        print("6 - Consultar Estilos de Jogo dos Jogadores")
        print("7 - Consultar Funcionários")
        print("8 - Consultar Estádios e Clubes")
        print("9 - Consultar Campeonatos")
        print("10 - Consultar Campeonatos e Associações")
        print("11 - Consultar Estatísticas dos Jogadores")
        print("X - Sair")

        escolha = input("Escolha uma opção: ").strip()

        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()

            if escolha == "1":
                mostrar_clubes(cursor)
            elif escolha == "2":
                mostrar_selecoes(cursor)
            elif escolha == "3":
                mostrar_jogadores(cursor)
            elif escolha == "4":
                mostrar_jogadores_contrato(cursor)
            elif escolha == "5":
                mostrar_jogadores_geral(cursor)
            elif escolha == "6":
                mostrar_jogadores_estilos(cursor)
            elif escolha == "7":
                mostrar_funcionarios(cursor)
            elif escolha == "8":
                mostrar_estadios_e_clubes(cursor)
            elif escolha == "9":
                mostrar_campeonatos(cursor)
            elif escolha == "10":
                mostrar_campeonatos_associacoes(cursor)
            elif escolha == "11":
                mostrar_estatisticas(cursor)
            else:
                break

            conexao.commit()
            cursor.close()
            conexao.close()

def fluxo_geral(cursor, conexao):
    """Realiza um fluxo geral de operações: criar clube, jogador, estádio, contrato, atributos, estilos de jogo, campeonato e estatísticas."""

    print("\n--- Iniciando o fluxo geral ---")

    # 1. Criar um clube
    while True:
        adicionar_clube = input("\nDeseja adicionar um clube? (s/n): ").strip().lower()
        if adicionar_clube == 's':
            print("\nCriando um clube:")
            id_clube = inserir_associacao(cursor, tipo="clube")
            inserir_clube(cursor, id_clube, conexao)
        elif adicionar_clube == 'n':
            print("Pulando a criação do clube...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 2. Criar um jogador
    while True:
        adicionar_jogador = input("\nDeseja adicionar um jogador? (s/n): ").strip().lower()
        if adicionar_jogador == 's':
            print("\nCriando um jogador:")
            inserir_jogador(cursor)
        elif adicionar_jogador == 'n':
            print("Pulando a criação do jogador...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 3. Atrelar um estádio ao clube
    while True:
        adicionar_estadio = input("\nDeseja atrelando um estádio ao clube? (s/n): ").strip().lower()
        if adicionar_estadio == 's':
            print("\nAtrelando um estádio ao clube:")
            inserir_estadio_a_clube(cursor, conexao)
        elif adicionar_estadio == 'n':
            print("Pulando a associação do estádio...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 4. Criar um contrato para o jogador
    while True:
        adicionar_contrato = input("\nDeseja criar um contrato para o jogador? (s/n): ").strip().lower()
        if adicionar_contrato == 's':
            print("\nCriando um contrato para o jogador:")
            inserir_contrato(cursor)
        elif adicionar_contrato == 'n':
            print("Pulando a criação do contrato...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 5. Criar atributos para o jogador
    while True:
        adicionar_atributos = input("\nDeseja criar atributos para o jogador? (s/n): ").strip().lower()
        if adicionar_atributos == 's':
            print("\nCriando atributos para o jogador:")
            inserir_atributos(cursor)
        elif adicionar_atributos == 'n':
            print("Pulando a criação dos atributos...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 6. Criar estilos de jogo e associar ao jogador
    while True:
        adicionar_estilo = input("\nDeseja adicionar um estilo de jogo ao jogador? (s/n): ").strip().lower()
        if adicionar_estilo == 's':
            inserir_estilo_de_jogo(cursor)
        elif adicionar_estilo == 'n':
            print("Continuando para o próximo passo...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 7. Criar um campeonato
    while True:
        adicionar_campeonato = input("\nDeseja criar um campeonato? (s/n): ").strip().lower()
        if adicionar_campeonato == 's':
            print("\nCriando um campeonato:")
            inserir_campeonato(cursor, conexao)
        elif adicionar_campeonato == 'n':
            print("Pulando a criação do campeonato...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    # 8. Inserir estatísticas para o jogador no campeonato
    while True:
        adicionar_estatisticas = input("\nDeseja inserir estatísticas para o jogador no campeonato? (s/n): ").strip().lower()
        if adicionar_estatisticas == 's':
            print("\nInserindo estatísticas para o jogador no campeonato:")
            inserir_estatisticas(cursor, conexao)
        elif adicionar_estatisticas == 'n':
            print("Pulando a inserção de estatísticas...")
            break
        else:
            print("Entrada inválida. Digite 's' para Sim ou 'n' para Não.")

    print("\n--- Fluxo geral concluído com sucesso! ---")

#wasd
if __name__ == "__main__":
    menu() 