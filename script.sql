-- Crear la base de datos para el proyecto
CREATE DATABASE IF NOT EXISTS peaje_arduino;

-- Usar la base de datos creada
USE peaje_arduino;

-- Crear tabla para almacenar los registros de paso de vehículos
CREATE TABLE IF NOT EXISTS registros_peaje (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp BIGINT,             -- Timestamp en milisegundos desde Arduino
    fecha_hora DATETIME,          -- Fecha y hora en formato legible
    distancia FLOAT,              -- Distancia detectada en cm
    duracion_paso INT,            -- Duración estimada del paso en ms
    hash_bloque VARCHAR(64)       -- Hash del bloque de la blockchain
);

-- Crear tabla para almacenar la blockchain
CREATE TABLE IF NOT EXISTS blockchain (
    indice INT PRIMARY KEY,       -- Índice del bloque en la cadena
    timestamp BIGINT,             -- Timestamp de creación del bloque
    datos TEXT,                   -- Datos almacenados en el bloque (en JSON)
    hash_anterior VARCHAR(64),    -- Hash del bloque anterior
    hash VARCHAR(64),             -- Hash del bloque actual
    nonce INT                     -- Valor usado para el minado
);

-- Crear un usuario para la aplicación (usar en entorno de desarrollo)
-- REEMPLAZAR 'contraseña' con una contraseña segura
CREATE USER IF NOT EXISTS 'usuario'@'localhost' IDENTIFIED BY 'contraseña';
GRANT ALL PRIVILEGES ON peaje_arduino.* TO 'usuario'@'localhost';
FLUSH PRIVILEGES;

-- Crear vistas para análisis de datos (opcional)
CREATE VIEW resumen_diario AS
SELECT 
    DATE(fecha_hora) AS fecha,
    COUNT(*) AS cantidad_vehiculos,
    MIN(fecha_hora) AS primera_deteccion,
    MAX(fecha_hora) AS ultima_deteccion
FROM 
    registros_peaje
GROUP BY 
    DATE(fecha_hora);