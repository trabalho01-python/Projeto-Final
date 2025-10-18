create database SuperSelect_sa;
use SuperSelect_sa;

create table usuarios (
id INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(150) NOT NULL,
email VARCHAR(200) UNIQUE NOT NULL,
senha VARCHAR(200) NOT NULL,
tipo ENUM('cliente','administrador') NOT NULL,

-- Campo específico para o administrador 
cpf VARCHAR(11) UNIQUE,
endereço VARCHAR(200) 
);