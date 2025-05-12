import serial
import mysql.connector
import hashlib
import json
from datetime import datetime
from time import sleep

class ArduinoSerialReader:
    def __init__(self, port='COM3', baudrate=9600):
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.config_mysql = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'arduino_peaje'
        }
    
    def get_db_connection(self):
        return mysql.connector.connect(**self.config_mysql)

    def calcular_hash(self, datos):
        return hashlib.sha256(json.dumps(datos).encode()).hexdigest()

    def guardar_registro(self, timestamp):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Crear datos del registro
            datos = {
                'timestamp': timestamp,
                'fecha_hora': datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Calcular hash del registro
            hash_registro = self.calcular_hash(datos)

            # Insertar en la tabla registros_peaje
            sql = """INSERT INTO registros_peaje (fecha_hora, hash) 
                    VALUES (%s, %s)"""
            cursor.execute(sql, (datos['fecha_hora'], hash_registro))
            
            # Si hay 10 registros nuevos, crear un nuevo bloque
            cursor.execute("SELECT COUNT(*) FROM registros_peaje WHERE bloque_id IS NULL")
            registros_pendientes = cursor.fetchone()[0]
            
            if registros_pendientes >= 10:
                self.crear_nuevo_bloque(cursor)
            
            conn.commit()

        except Exception as e:
            print(f"Error al guardar registro: {str(e)}")
        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()

    def crear_nuevo_bloque(self, cursor):
        try:
            # Obtener último bloque
            cursor.execute("SELECT * FROM blockchain ORDER BY indice DESC LIMIT 1")
            ultimo_bloque = cursor.fetchone()
            
            # Obtener registros pendientes
            cursor.execute("SELECT * FROM registros_peaje WHERE bloque_id IS NULL LIMIT 10")
            registros = cursor.fetchall()
            
            # Crear nuevo bloque
            indice = 1 if not ultimo_bloque else ultimo_bloque[0] + 1
            timestamp = datetime.now().timestamp()
            datos = json.dumps([dict(zip(['id', 'fecha_hora', 'hash'], r)) for r in registros])
            hash_anterior = '0' if not ultimo_bloque else ultimo_bloque[2]
            nonce = 0
            
            # Proof of Work simple
            while True:
                hash_bloque = hashlib.sha256(
                    f"{indice}{timestamp}{datos}{hash_anterior}{nonce}".encode()
                ).hexdigest()
                if hash_bloque.startswith('00'):  # Dificultad de minado
                    break
                nonce += 1
            
            # Insertar nuevo bloque
            sql = """INSERT INTO blockchain 
                    (indice, timestamp, datos, hash_anterior, hash, nonce) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (indice, timestamp, datos, hash_anterior, hash_bloque, nonce))
            
            # Actualizar registros con el ID del bloque
            bloque_id = cursor.lastrowid
            cursor.execute(
                "UPDATE registros_peaje SET bloque_id = %s WHERE bloque_id IS NULL LIMIT 10",
                (bloque_id,)
            )

        except Exception as e:
            print(f"Error al crear bloque: {str(e)}")
            raise e

    def start_reading(self):
        print("Iniciando lectura del puerto serial...")
        try:
            while True:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    
                    if line.startswith('VEHICULO_DETECTADO'):
                        _, timestamp = line.split(',')
                        self.guardar_registro(int(timestamp))
                        print(f"Vehículo detectado: {timestamp}")
                        
                sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nLectura interrumpida por el usuario")
        finally:
            self.serial_port.close()

if __name__ == '__main__':
    reader = ArduinoSerialReader()
    reader.start_reading()