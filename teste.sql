CREATE DATABASE trabalho;
#drop database trabalho;
USE trabalho;
#show databases;
#CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin40028922';
GRANT ALL PRIVILEGES ON trabalho.* TO 'admin'@'localhost' WITH GRANT OPTION;

#CREATE USER 'user'@'localhost' IDENTIFIED BY 'user321';
GRANT SELECT, INSERT ON trabalho.* TO 'user'@'localhost';


CREATE TABLE associacoes_esportivas (
    id_associacao INT AUTO_INCREMENT PRIMARY KEY,
    sigla VARCHAR(3) NOT NULL,
    apelido VARCHAR(20),
    qualidade DECIMAL(3,2) CHECK (qualidade BETWEEN 0.0 AND 05.00),
    nome VARCHAR(45) NOT NULL,
    mascote VARCHAR(20),
    formacao VARCHAR(10) NOT NULL,
    tipo varchar(10) not null CHECK (tipo = 'clube' or tipo = 'selecao')
);

CREATE TABLE cidades(
    id_cidade INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45) NOT NULL
);

CREATE TABLE clubes(
    id_associacao INT PRIMARY KEY NOT NULL,
    receita FLOAT NOT NULL CHECK (receita BETWEEN 0 AND 1000000000),
    id_cidade INT NOT NULL,
    pais VARCHAR(45) NOT NULL,
    FOREIGN KEY (id_associacao) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE,
    FOREIGN KEY (id_cidade) REFERENCES cidades(id_cidade)
);

CREATE TABLE selecoes(
    id_associacao INT PRIMARY KEY NOT NULL,
    FOREIGN KEY (id_associacao) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE
);

-- trabalho feito até aq

CREATE TABLE estadios(
    id_estadio INT AUTO_INCREMENT PRIMARY KEY,
    capacidade INT NOT NULL CHECK (capacidade BETWEEN 1000 AND 100000),
    nome VARCHAR(60) NOT NULL
);

CREATE TABLE clube_estadios(
    id_estadio INT NOT NULL,
    id_associacao INT NOT NULL,
    PRIMARY KEY (id_estadio, id_associacao),
    FOREIGN KEY (id_associacao) REFERENCES clubes(id_associacao) ON DELETE CASCADE,
    FOREIGN KEY (id_estadio) REFERENCES estadios(id_estadio) ON DELETE CASCADE
);

CREATE TABLE estilos_de_jogo(
    id_estilo INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45)
);

CREATE TABLE jogadores(
    id_jogador INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45) NOT NULL,
    posicao VARCHAR(3) NOT NULL CHECK (posicao IN ('GOL', 'ZAG', 'LE', 'LD', 'ADE', 'ADD', 'VOL', 'MC', 'ME', 'MD', 'MEI', 'PE', 'PD', 'SA', 'ATA')),
    id_selecao INT NOT NULL,
    FOREIGN KEY (id_selecao) REFERENCES selecoes(id_associacao)
);

CREATE TABLE estilos_de_jogo_jogadores(
    id_estilo INT NOT NULL,
    id_jogador INT NOT NULL,
    PRIMARY KEY (id_estilo, id_jogador),
    FOREIGN KEY (id_estilo) REFERENCES estilos_de_jogo(id_estilo) ON DELETE CASCADE,
    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
);

CREATE TABLE contratos(
    id_contrato INT AUTO_INCREMENT PRIMARY KEY,
    salario FLOAT NOT NULL CHECK (salario > 0 AND salario <= 10000000),
    data_inicial DATE NOT NULL,
    duracao DATE NOT NULL,
    bonus DECIMAL(8,2),
    luvas DECIMAL(8,2),
    multarecisoria DECIMAL(8,2),
    numero INT NOT NULL,
    id_jogador INT NOT NULL,
    id_associacao INT NOT NULL,
    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE,
    FOREIGN KEY (id_associacao) REFERENCES clubes(id_associacao) ON DELETE CASCADE
);

DELIMITER //
CREATE TRIGGER verifica_duracao_contrato
BEFORE INSERT ON contratos
FOR EACH ROW
BEGIN
    IF NEW.data_inicial >= NEW.duracao THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: A data inicial do contrato deve ser anterior à data de término (duracao).';
    END IF;
END;
//
DELIMITER ;


CREATE TABLE atributos (
    id_atributo INT AUTO_INCREMENT PRIMARY KEY,
    drible DECIMAL(4,2) NOT NULL CHECK (drible BETWEEN 0 AND 100),
    ritmo DECIMAL(4,2) NOT NULL CHECK (ritmo BETWEEN 0 AND 100),
    fisico DECIMAL(4,2) NOT NULL CHECK (fisico BETWEEN 0 AND 100),
    passe DECIMAL(4,2) NOT NULL CHECK (passe BETWEEN 0 AND 100),
    chute DECIMAL(4,2) NOT NULL CHECK (chute BETWEEN 0 AND 100),
    defesa DECIMAL(4,2) NOT NULL CHECK (defesa BETWEEN 0 AND 100),
    geral INT NOT NULL CHECK (geral BETWEEN 0 AND 100),
    id_jogador INT NOT NULL,
    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
);

CREATE TABLE campeonatos(
    id_campeonato INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(60) NOT NULL
);

CREATE TABLE campeonatos_associacoes(
    id_campeonato INT NOT NULL,
    id_associacao INT NOT NULL,
    classificacao INT NOT NULL CHECK (classificacao BETWEEN 1 AND 100),
    PRIMARY KEY (id_campeonato, id_associacao),
    FOREIGN KEY (id_campeonato) REFERENCES campeonatos(id_campeonato) ON DELETE CASCADE,
    FOREIGN KEY (id_associacao) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE
);

CREATE TABLE estatisticas(
    id_estatistica INT AUTO_INCREMENT PRIMARY KEY,
    gol INT CHECK (gol >= 0),
    assist INT CHECK (assist >= 0),
    nota_jogo DECIMAL(3,2) CHECK (nota_jogo BETWEEN 0 AND 10),
    cartao_ver INT CHECK (cartao_ver BETWEEN 0 AND 2),
    cartao_ama INT CHECK (cartao_ama BETWEEN 0 AND 5),
    id_jogador INT NOT NULL,
    id_campeonato INT NOT NULL,
    numero_jogos INT CHECK (numero_jogos >= 0),
    FOREIGN KEY (id_campeonato) REFERENCES campeonatos(id_campeonato) ON DELETE CASCADE,
    FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador) ON DELETE CASCADE
);

CREATE TABLE partidas(
    id_partida INT AUTO_INCREMENT PRIMARY KEY,
    tempo TIME,
    resultado INT,
    id_campeonato INT,
    id_mandante INT,
    id_visitante INT,
    FOREIGN KEY (id_campeonato) REFERENCES campeonatos(id_campeonato) ON DELETE CASCADE,
    FOREIGN KEY (id_mandante) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE,
    FOREIGN KEY (id_visitante) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE
);

CREATE TABLE cargos(
    id_cargo INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(40) NOT NULL
);

CREATE TABLE funcionarios(
    id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(45) NOT NULL,
    qualidade DECIMAL(3,2) NOT NULL CHECK (qualidade BETWEEN 0.00 AND 05.00),
    id_associacao INT NOT NULL,
    id_cargo INT NOT NULL,
    id_nacionalidade INT NOT NULL,
    FOREIGN KEY (id_associacao) REFERENCES associacoes_esportivas(id_associacao) ON DELETE CASCADE,
    FOREIGN KEY (id_nacionalidade) REFERENCES selecoes(id_associacao),
    FOREIGN KEY (id_cargo) REFERENCES cargos(id_cargo)
);
#select * from cidades;
#select * from associacoes_esportivas;
#select * from clubes;
#SELECT * FROM clubes c left JOIN associacoes_esportivas a ON a.id_associacao = c.id_associacao JOIN cidades ci ON ci.id_cidade = c.id_cidade;