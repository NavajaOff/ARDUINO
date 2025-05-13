import serial
import time
from serial.tools import list_ports
import mysql.connector
import hashlib
import json
from datetime import datetime

# Configuración de MySQL
config_mysql = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'arduino_peaje',
    'raise_on_warnings': True
}

def calcular_hash(datos):
    return hashlib.sha256(json.dumps(datos).encode()).hexdigest()

def guardar_distancia(cursor, distancia):
    try:
        # Solo guardar si se detecta un vehículo (distancia < 25cm)
        if distancia < 25:
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Datos para registros_peaje
            datos_peaje = {
                'fecha_hora': fecha_hora,
                'estado': "VEHICULO DETECTADO",
                'distancia': distancia
            }
            
            # Calcular hash del registro
            hash_registro = calcular_hash(datos_peaje)

            # 1. Insertar en la tabla registros_peaje
            sql_peaje = """INSERT INTO registros_peaje (fecha_hora, estado, hash) 
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql_peaje, (fecha_hora, datos_peaje['estado'], hash_registro))
            
            # 2. Insertar en la tabla distancias
            sql_distancias = """INSERT INTO distancias (fecha_hora, distancia, hash) 
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql_distancias, (fecha_hora, distancia, hash_registro))
            
            # 3. Crear bloque cada 5 registros
            cursor.execute("SELECT COUNT(*) FROM registros_peaje WHERE bloque_id IS NULL")
            registros_sin_bloque = cursor.fetchone()[0]
            
            if registros_sin_bloque >= 5:
                crear_nuevo_bloque(cursor)
            
            print(f"✅ Vehículo detectado y registrado - Distancia: {distancia} cm")
            return True
        else:
            print(f"ℹ️ No se detectó vehículo - Distancia: {distancia} cm")
            return False

    except Exception as e:
        print(f"❌ Error al guardar registro: {str(e)}")
        return False

def crear_nuevo_bloque(cursor):
    try:
        # Obtener registros sin bloque
        cursor.execute("""
            SELECT id, fecha_hora, estado, hash 
            FROM registros_peaje 
            WHERE bloque_id IS NULL 
            ORDER BY id
            LIMIT 5
        """)
        registros = cursor.fetchall()
        
        # Obtener último bloque
        cursor.execute("SELECT * FROM blockchain ORDER BY indice DESC LIMIT 1")
        ultimo_bloque = cursor.fetchone()
        
        # Preparar datos del nuevo bloque
        indice = 1 if not ultimo_bloque else ultimo_bloque[0] + 1
        timestamp = datetime.now().timestamp()
        datos = {
            'registros': [
                {
                    'id': reg[0],
                    'fecha_hora': reg[1].strftime('%Y-%m-%d %H:%M:%S'),
                    'estado': reg[2],
                    'hash': reg[3]
                } for reg in registros
            ]
        }
        hash_anterior = '0' * 64 if not ultimo_bloque else ultimo_bloque[4]
        
        # Encontrar nonce válido
        nonce = 0
        while True:
            bloque = {
                'indice': indice,
                'timestamp': timestamp,
                'datos': json.dumps(datos),
                'hash_anterior': hash_anterior,
                'nonce': nonce
            }
            hash_bloque = hashlib.sha256(str(bloque).encode()).hexdigest()
            if hash_bloque.startswith('00'):  # Dificultad básica
                break
            nonce += 1
        
        # Insertar nuevo bloque
        sql = """INSERT INTO blockchain 
                (indice, timestamp, datos, hash_anterior, hash, nonce) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (indice, timestamp, json.dumps(datos), 
                           hash_anterior, hash_bloque, nonce))
        
        # Actualizar registros con el ID del bloque
        ids_registros = [reg[0] for reg in registros]
        cursor.execute("""
            UPDATE registros_peaje 
            SET bloque_id = %s 
            WHERE id IN ({})
        """.format(','.join(['%s'] * len(ids_registros))), 
        [indice] + ids_registros)
        
        print(f"✅ Nuevo bloque creado: {indice}")
        
    except Exception as e:
        print(f"❌ Error al crear bloque: {str(e)}")
        raise e

def read_and_save():
    # Listar puertos disponibles
    print("Puertos seriales disponibles:")
    ports = list_ports.comports()
    for port in ports:
        print(f"- {port.device}: {port.description}")
    
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        print("✅ Conexión a la base de datos establecida")

        # Conectar al Arduino
        print("\nIntentando conectar al Arduino en COM3...")
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # Esperar a que se establezca la conexión
        
        print("✅ Conexión al Arduino establecida")
        print("📊 Leyendo y guardando datos (presiona Ctrl+C para detener)...")
        
        while True:
            if arduino.in_waiting:
                try:
                    line = arduino.readline().decode('utf-8').strip()
                    
                    if line.startswith('Distance:'):
                        distancia = float(line.split(':')[1].split('cm')[0].strip())
                        if guardar_distancia(cursor, distancia):
                            conn.commit()
                except Exception as e:
                    print(f"❌ Error al procesar línea: {str(e)}")
            
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n⚠️ Lectura interrumpida por el usuario")
    except serial.SerialException as e:
        print(f"\n❌ Error de conexión serial: {e}")
        print("\nVerifica que:")
        print("1. El Arduino esté conectado físicamente")
        print("2. El puerto COM3 sea el correcto")
        print("3. No haya otro programa usando el puerto")
    except mysql.connector.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
    finally:
        print("\nCerrando conexiones...")
        if 'arduino' in locals():
            arduino.close()
            print("✅ Conexión serial cerrada")
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("✅ Conexión a base de datos cerrada")

if __name__ == "__main__":
    read_and_save()