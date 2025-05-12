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
        # Crear datos del registro
        datos = {
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'distancia': distancia
        }
        
        # Calcular hash del registro
        hash_registro = calcular_hash(datos)

        # Insertar en la tabla distancias
        sql = """INSERT INTO distancias (fecha_hora, distancia, hash) 
                VALUES (%s, %s, %s)"""
        cursor.execute(sql, (datos['fecha_hora'], distancia, hash_registro))
        
        print(f"✅ Distancia guardada: {distancia} cm")
        return True

    except Exception as e:
        print(f"❌ Error al guardar distancia: {str(e)}")
        return False

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
                    print(f"📡 Dato recibido: {line}")
                    
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