USE arduino_peaje;

-- Crear tabla blockchain
CREATE TABLE IF NOT EXISTS blockchain (
    indice INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    timestamp DOUBLE NOT NULL,
    datos TEXT NOT NULL,
    hash_anterior VARCHAR(64) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    nonce INT NOT NULL
);

-- Crear tabla distancias (con timestamp incluido)
CREATE TABLE IF NOT EXISTS distancias (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME,
    distancia FLOAT,
    hash VARCHAR(64),
    timestamp BIGINT
);

-- Crear tabla registros_peaje
CREATE TABLE IF NOT EXISTS registros_peaje (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL,
    estado VARCHAR(50),
    hash VARCHAR(64) NOT NULL,
    bloque_id INT,
    FOREIGN KEY (bloque_id) REFERENCES blockchain(indice)
);