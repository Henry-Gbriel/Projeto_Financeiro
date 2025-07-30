CREATE DATABASE projeto_acesso;

USE projeto_acesso;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(800) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cargo VARCHAR(100),
    senha VARCHAR(255)
);

select * from usuarios;

DROP DATABASE projeto_acesso;
