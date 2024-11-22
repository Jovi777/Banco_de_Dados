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

#funções para alterar daqui p baixo é vc...

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

#daq p baixo sou eu

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
    print(f"Atributos do jogador '{nome_jogador}' inseridos com sucesso!")

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

#termina aq

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

#funcoes alterar

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
    
    print(f"Atributos do jogador '{nome_jogador}' atualizados com sucesso!")

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


# possiveis funções:
'''
Inserir estadio, atrelar estadio a um clube FEITO
Inserir contrato, atrelar jogador a um clube FEITO
Inserir Atributos, atribuir atributos ao jogador FEITO
Inserir Estilo de jogo, atribuir estilo de jogo ao jogador FEITO
Inserir Campeonatos, adicionar campeonato FEITO
Inserir times em campeonatos, add time e campeonato caso ñ existam +- FEITO
Inserir estatisticas, add campeonato e add jogador 
Inserir partidas, add clubes e campeonatos e add clubes aos campeonatos caso campeonato not null      +- FEITO
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
        print("5 - Inserir Estadio a um clube")
        print("6 - Inserir Campeonato")
        print("7 - Inserir Associacao a um Campeonato")
        print("8 - Inserir Partidas a um Campeonato")
        print("9 - Inserir Atributos")
        print("10 - Inserir Contratos")
        print("11 - Inserir Estilo de jogo")
        print("12 - Inserir Funcionario ")
        print("13 - Inserir Estatisticas")
        print("14 - Alterar Clube ")
        print("15 - Alterar Selecao ")
        print("16 - Alterar Jogador ")
        print("17 - Alterar Estadio a um clube ")
        print("18 - Alterar Contrato")
        print("19 - Alterar Atributos")
        print("20 - Alterar Estilo de jogo")
        print("X - SAIR")

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
                #Criar campeonato dale Vasco
                inserir_campeonato(cursor, conexao)

            elif escolha == "7":
                nome_campeonato = input("Digite o nome do campeonato ao qual deseja adicionar associações: ").title()
                inserir_associacoes_campeonato(cursor, conexao, nome_campeonato)

            elif escolha == "8":
                nome_campeonato = input("Digite o nome do campeonato para adicionar partidas: ").title()
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

            elif escolha == "14":
                alterar_clube(cursor, conexao)

            elif escolha == "15":
                alterar_selecao(cursor, conexao)

            elif escolha == "16":
                alterar_jogador(cursor, conexao)

            elif escolha == "17":
                alterar_estadio(cursor, conexao)

            elif escolha == "18":
                alterar_contrato(cursor, conexao)

            elif escolha == "19":
                alterar_atributos(cursor, conexao)
            
            elif escolha == "20":
                alterar_estilo_de_jogo(cursor, conexao)

            else:
                print("Saindo do programa...")
                break

            conexao.commit()  # Confirma todas as alterações no banco
            cursor.close()
            conexao.close()
#wasd
if __name__ == "__main__":
    menu() 