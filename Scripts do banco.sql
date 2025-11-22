create database SuperSelect_sa;
use SuperSelect_sa;

create table usuarios (
id INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(150) NOT NULL,
email VARCHAR(200) UNIQUE NOT NULL,
senha VARCHAR(200) NOT NULL,
cpf VARCHAR(11) UNIQUE,
tipo ENUM('cliente','administrador') NOT NULL,

-- Campo específico para o administrador 
endereco VARCHAR(200) DEFAULT("Não informado")
);

create table produtos (
id INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(250) NOT NULL,
descricao TEXT NOT NULL,
categoria ENUM('alimentos','bebidas','higiene','limpeza','hortifruti','padaria') NOT NULL,
preco DECIMAL(10,2) NOT NULL,
data_validade DATE,
sem_validade BOOLEAN DEFAULT 0,
estoque INT DEFAULT 0,
imagem VARCHAR(1000) 
);

create table comentarios_adm (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
produto_id INT NOT NULL,
parent_id INT NULL, 
comentario TEXT NOT NULL,
data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
FOREIGN KEY (parent_id) REFERENCES comentarios_adm(id)
);

ALTER TABLE comentarios_adm
DROP FOREIGN KEY comentarios_adm_ibfk_3;

ALTER TABLE comentarios_adm
ADD CONSTRAINT fk_parent_id
FOREIGN KEY (parent_id) REFERENCES comentarios_adm(id) ON DELETE CASCADE;


INSERT INTO produtos (nome, descricao, categoria, preco, data_validade, sem_validade, estoque, imagem)
VALUES (
    'Leite Integral',
    'Leite integral fresco, 1 litro',
    'bebidas',
    5.50,
    '2025-12-31',
    0,
    50,
    'https://diafoodservice.agilecdn.com.br/13346_1.jpg'
);

INSERT INTO usuarios (nome, email, senha, cpf, tipo)
VALUES (
    'Ana Silva',
    'ana.silva@email.com',
    '1234',
    '12345676754',
    'cliente'
);

INSERT INTO usuarios (nome, email, senha, cpf, tipo, endereco)
VALUES (
    'Maria',
    'maria@email.com',
    '1234',
    '76543798654',
    'administrador',
    'Rua Central, 50'
);