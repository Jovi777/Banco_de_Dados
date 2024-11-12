import mysql.connector
from mysql.connector import Error

'''
con = mysql.connector.connect(
  user='admin',
  password='admin40028922',
  host='localhost',
  database='trabalho'
)
if con.is_connected():
  print ('conectado no BD')
else:
  print ('conexão falhou')
'''



def inserir_associacao():
    try:
        # Conecta ao banco de dados
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',          # Usuário com permissões
            password='1826',
            database='trabalho'
        )
        
        if conexao.is_connected():
            cursor = conexao.cursor()
            
            # Solicita e valida os dados do usuário
            sigla = input("Digite a sigla da associação (3 caracteres): ")
            apelido = input("Digite o apelido da associação: ")
            
            # Validação do valor de qualidade para garantir que está entre 0.00 e 10.00 com duas casas decimais
            while True:
                try:
                    qualidade = float(input("Digite a qualidade da associação (0.00 a 5.00): "))
                    if 0.00 <= qualidade <= 5.00:
                        qualidade = round(qualidade, 2)  # Limita a duas casas decimais
                        break
                    else:
                        print("Qualidade deve estar entre 0.00 e 10.00.")
                except ValueError:
                    print("Por favor, insira um número válido para a qualidade.")
            
            nome = input("Digite o nome da associação: ")
            mascote = input("Digite o mascote da associação: ")
            formacao = input("Digite a formação da associação: ")
            
            # Comando SQL para inserção de dados
            sql = """
                INSERT INTO associacoes_esportivas (sigla, apelido, qualidade, nome, mascote, formacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Valores a serem inseridos
            valores = (sigla, apelido, qualidade, nome, mascote, formacao)
            
            # Executa o comando
            cursor.execute(sql, valores)
            conexao.commit()
            print("Associação esportiva inserida com sucesso!")
    
    except Error as e:
        print(f"Erro ao conectar ou inserir no banco de dados: {e}")
    
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Chama a função para inserir uma nova associação esportiva
inserir_associacao()


  