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

create table comentarios (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
produto_id INT NOT NULL,
comentario TEXT NOT NULL,
data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
FOREIGN KEY (produto_id) REFERENCES produtos(id)
);