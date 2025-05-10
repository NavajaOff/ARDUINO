import serial
import hashlib
import datetime
import mysql.connector
import json
import time

# Configuración de la conexión serial con Arduino
PUERTO_SERIAL = 'COM3'  # Cambiar según tu puerto
VELOCIDAD = 9600

# Configuración de la conexión MySQL
config_mysql = {
    'user': 'usuario',
    'password': 'contraseña',
    'host': 'localhost',
    'database': 'peaje_arduino',
    'raise_on_warnings': True
}

# Clase simple para implementar blockchain
class Bloque:
    def __init__(self, indice, timestamp, datos, hash_anterior):
        self.indice = indice
        self.timestamp = timestamp
        self.datos = datos
        self.hash_anterior = hash_anterior
        self.nonce = 0
        self.hash = self.calcular_hash()
    
    def calcular_hash(self):
        # Crear un hash combinando todos los datos del bloque
        bloque_string = str(self.indice) + str(self.timestamp) + str(self.datos) + str(self.hash_anterior) + str(self.nonce)
        return hashlib.sha256(bloque_string.encode()).hexdigest()
    
    def minar_bloque(self, dificultad=2):
        # Implementación simple de prueba de trabajo
        while self.hash[:dificultad] != '0' * dificultad:
            self.nonce += 1
            self.hash = self.calcular_hash()

class Blockchain:
    def __init__(self):
        # Crear bloque génesis
        self.cadena = [self.crear_bloque_genesis()]
        self.dificultad = 2  # Dificultad para minado
    
    def crear_bloque_genesis(self):
        return Bloque(0, datetime.datetime.now().timestamp(), "Bloque Génesis", "0")
    
    def obtener_ultimo_bloque(self):
        return self.cadena[-1]
    
    def agregar_bloque(self, datos):
        # Crear nuevo bloque
        indice = len(self.cadena)
        timestamp = datetime.datetime.now().timestamp()
        hash_anterior = self.obtener_ultimo_bloque().hash
        nuevo_bloque = Bloque(indice, timestamp, datos, hash_anterior)
        
        # Minar el bloque antes de agregarlo
        nuevo_bloque.minar_bloque(self.dificultad)
        self.cadena.append(nuevo_bloque)
        return nuevo_bloque
    
    def es_cadena_valida(self):
        # Verificar integridad de la cadena
        for i in range(1, len(self.cadena)):
            bloque_actual = self.cadena[i]
            bloque_anterior = self.cadena[i-1]
            
            # Verificar hash
            if bloque_actual.hash != bloque_actual.calcular_hash():
                return False
            
            # Verificar enlace de hash
            if bloque_actual.hash_anterior != bloque_anterior.hash:
                return False
        
        return True

# Inicializar la blockchain
blockchain_peaje = Blockchain()

# Crear tablas en MySQL si no existen
def inicializar_bd():
    try:
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        # Tabla para registros de paso de vehículos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros_peaje (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp BIGINT,
            fecha_hora DATETIME,
            hash_bloque VARCHAR(64)
        )
        ''')
        
        # Tabla para la blockchain
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            indice INT PRIMARY KEY,
            timestamp BIGINT,
            datos TEXT,
            hash_anterior VARCHAR(64),
            hash VARCHAR(64),
            nonce INT
        )
        ''')
        
        conn.commit()
        print("Base de datos inicializada correctamente")
    except mysql.connector.Error as err:
        print(f"Error al inicializar la BD: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Guardar registro en MySQL y en blockchain
def guardar_registro(timestamp):
    try:
        # Convertir timestamp a datetime para MySQL
        fecha_hora = datetime.datetime.fromtimestamp(timestamp/1000)  # Arduino envía en milisegundos
        
        # Datos para el bloque
        datos = {
            "timestamp": timestamp,
            "fecha_hora": fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            "tipo": "paso_vehiculo"
        }
        
        # Agregar a blockchain
        nuevo_bloque = blockchain_peaje.agregar_bloque(json.dumps(datos))
        
        # Guardar en MySQL
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        # Insertar en registros_peaje
        cursor.execute(
            "INSERT INTO registros_peaje (timestamp, fecha_hora, hash_bloque) VALUES (%s, %s, %s)",
            (timestamp, fecha_hora, nuevo_bloque.hash)
        )
        
        # Insertar bloque en tabla blockchain
        cursor.execute(
            "INSERT INTO blockchain (indice, timestamp, datos, hash_anterior, hash, nonce) VALUES (%s, %s, %s, %s, %s, %s)",
            (nuevo_bloque.indice, nuevo_bloque.timestamp, json.dumps(datos), nuevo_bloque.hash_anterior, nuevo_bloque.hash, nuevo_bloque.nonce)
        )
        
        conn.commit()
        print(f"Registro guardado con éxito - Hash: {nuevo_bloque.hash[:10]}...")
    except mysql.connector.Error as err:
        print(f"Error al guardar registro: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Función principal
def main():
    # Inicializar la base de datos
    inicializar_bd()
    
    try:
        # Conectar con Arduino
        arduino = serial.Serial(PUERTO_SERIAL, VELOCIDAD, timeout=1)
        print(f"Conectado a Arduino en {PUERTO_SERIAL}")
        time.sleep(2)  # Esperar a que se estabilice la conexión
        
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').rstrip()
                print(f"Recibido de Arduino: {linea}")
                
                # Procesar datos recibidos
                if "VEHICULO_DETECTADO" in linea:
                    partes = linea.split(',')
                    if len(partes) == 2:
                        timestamp = int(partes[1])
                        guardar_registro(timestamp)
                # También podemos procesar la información de distancia para análisis
                elif "Distance:" in linea:
                    try:
                        # Extraer el valor de distancia
                        distancia = float(linea.split("Distance:")[1].split("cm")[0].strip())
                        print(f"Distancia registrada: {distancia} cm")
                        # Opcionalmente, podríamos guardar estos datos en otra tabla
                    except Exception as e:
                        print(f"Error al procesar distancia: {e}")
                
            time.sleep(0.1)
    
    except serial.SerialException as e:
        print(f"Error de conexión serial: {e}")
    except KeyboardInterrupt:
        print("Programa terminado por el usuario")
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("Conexión con Arduino cerrada")

if __name__ == "__main__":
    main()