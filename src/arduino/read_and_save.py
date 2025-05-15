from src.config.conexion import config_mysql
import serial
import time
from serial.tools import list_ports
import mysql.connector
import hashlib
import json
from datetime import datetime
from flask import current_app
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class ArduinoConnection:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.last_status = None
        self.vehiculo_en_proceso = False  # Nueva variable para controlar el estado
        self.last_detection_time = 0  # Tiempo de la última detección

    def connect(self):
        try:
            if not self.is_connected:
                self.connection = serial.Serial('COM3', 9600)
                time.sleep(2)  # Esperar a que se establezca la conexión
                if self.connection.is_open:
                    self.is_connected = True
                    if self.last_status != "connected":
                        print("¡Conexión establecida!")
                        self.last_status = "connected"
                return True
        except Exception as e:
            if self.last_status != "error":
                print(f"❌ Error de conexión: {e}")
                self.last_status = "error"
            self.is_connected = False
            return False

    def disconnect(self):
        if self.connection and self.is_connected:
            self.connection.close()
            self.is_connected = False
            if self.last_status != "closed":
                print("Conexión cerrada.")
                self.last_status = "closed"

    def read_data(self):
        if self.is_connected and self.connection:
            try:
                if self.connection.in_waiting:
                    return self.connection.readline().decode('utf-8').strip()
            except Exception as e:
                self.disconnect()
                return None
        return None

def calcular_hash(datos):
    return hashlib.sha256(json.dumps(datos).encode()).hexdigest()

def guardar_distancia(cursor, distancia, app):
    try:
        # Variable estática para controlar el estado del vehículo
        if not hasattr(guardar_distancia, "vehiculo_en_proceso"):
            guardar_distancia.vehiculo_en_proceso = False
            guardar_distancia.tiempo_ultima_deteccion = 0

        tiempo_actual = datetime.now().timestamp()
        
        # Solo guardar si se detecta un vehículo (distancia < 25cm)
        if distancia < 25:
            # Si no hay un vehículo en proceso, registrar uno nuevo
            if not guardar_distancia.vehiculo_en_proceso:
                fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Datos para registros_peaje
                datos_peaje = {
                    'fecha_hora': fecha_hora,
                    'estado': "VEHICULO DETECTADO",
                    'distancia': distancia
                }
                
                # Calcular hash del registro
                hash_registro = calcular_hash(datos_peaje)

                # Insertar en las tablas
                sql_peaje = """INSERT INTO registros_peaje (fecha_hora, estado, hash) 
                        VALUES (%s, %s, %s)"""
                cursor.execute(sql_peaje, (fecha_hora, datos_peaje['estado'], hash_registro))
                
                sql_distancias = """INSERT INTO distancias (fecha_hora, distancia, hash) 
                        VALUES (%s, %s, %s)"""
                cursor.execute(sql_distancias, (fecha_hora, distancia, hash_registro))
                
                # Verificar si se debe crear un nuevo bloque
                cursor.execute("SELECT COUNT(*) FROM registros_peaje WHERE bloque_id IS NULL")
                registros_sin_bloque = cursor.fetchone()[0]
                
                if registros_sin_bloque >= 5:
                    crear_nuevo_bloque(cursor)
                
                print(f"✅ Vehículo detectado y registrado - Distancia: {distancia} cm")
                guardar_distancia.vehiculo_en_proceso = True
                guardar_distancia.tiempo_ultima_deteccion = tiempo_actual
                
                # Emitir evento de nuevo registro dentro del contexto de la aplicación
                with app.app_context():
                    try:
                        data = {
                            'type': 'new_registro',
                            'stats': obtener_estadisticas(),
                            'trafico': obtener_trafico_por_hora(),
                            'estadisticas': obtener_estadisticas_diarias(),
                            'bloques': obtener_ultimos_bloques()
                        }
                        print("Broadcasting update after new registro")
                        app.broadcast(data)
                    except Exception as e:
                        print(f"Error broadcasting update: {e}")
                
                return True
            else:
                # Si hay un vehículo en proceso, solo actualizar el tiempo
                guardar_distancia.tiempo_ultima_deteccion = tiempo_actual
                return False
        else:
            # Si la distancia es mayor a 25cm, resetear el estado inmediatamente
            if guardar_distancia.vehiculo_en_proceso:
                print(f"ℹ️ Vehículo salió del sensor - Distancia: {distancia} cm")
                guardar_distancia.vehiculo_en_proceso = False
                return True
            
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

def obtener_estadisticas():
    """
    Obtiene estadísticas generales de los vehículos detectados.
    Returns:
        dict: Diccionario con las estadísticas básicas
    """
    try:
        # Usar la configuración MySQL directamente
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
            
        # Obtener total de registros
        cursor.execute("""
            SELECT 
                COUNT(*) as total_registros,
                COUNT(CASE WHEN DATE(fecha_hora) = CURDATE() THEN 1 END) as registros_hoy,
                COUNT(CASE WHEN fecha_hora >= NOW() - INTERVAL 24 HOUR THEN 1 END) as registros_24h
            FROM registros_peaje
        """)
        total_registros, registros_hoy, registros_24h = cursor.fetchone()

        # Obtener integridad de la blockchain
        cursor.execute("SELECT COUNT(*) FROM blockchain")
        total_bloques = cursor.fetchone()[0]

        # Obtener último registro
        cursor.execute("""
            SELECT id, fecha_hora, hash 
            FROM registros_peaje 
            ORDER BY fecha_hora DESC 
            LIMIT 1
        """)
        ultimo_reg = cursor.fetchone()
        ultimo_registro = {
            'id': ultimo_reg[0],
            'fecha_hora': ultimo_reg[1].isoformat() if ultimo_reg else None,
            'hash': ultimo_reg[2]
        } if ultimo_reg else None

        return {
            'total_registros': total_registros,
            'total_bloques': total_bloques,
            'registros_24h': registros_24h,
            'ultimo_registro': ultimo_registro,
            'ultima_actualizacion': datetime.now().isoformat()
        }
            
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return {
            'total_registros': 0,
            'total_bloques': 0,
            'registros_24h': 0,
            'ultimo_registro': None,
            'ultima_actualizacion': datetime.now().isoformat(),
            'error': True
        }
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def obtener_trafico_por_hora():
    """
    Devuelve la cantidad de vehículos detectados agrupados por hora del día actual.
    Returns:
        list: Lista de diccionarios con 'hora' y 'cantidad'
    """
    try:
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                HOUR(fecha_hora) as hora, 
                COUNT(*) as cantidad
            FROM registros_peaje
            WHERE DATE(fecha_hora) = CURDATE()
            GROUP BY HOUR(fecha_hora)
            ORDER BY hora
        """)
        resultados = cursor.fetchall()
        return [{'hora': int(row[0]), 'cantidad': int(row[1])} for row in resultados]
    
    except Exception as e:
        print(f"Error al obtener tráfico por hora: {str(e)}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def obtener_estadisticas_diarias():
    try:
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(fecha_hora) as fecha,
                COUNT(*) as total
            FROM registros_peaje
            WHERE fecha_hora >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha_hora)
            ORDER BY fecha DESC
        """)
        
        return [{'fecha': row[0].isoformat(), 'total': row[1]} for row in cursor.fetchall()]
    
    except Exception as e:
        print(f"Error obteniendo estadísticas diarias: {str(e)}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def obtener_ultimos_bloques(page=1, limit=10):
    try:
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor(dictionary=True)
        
        # Obtener total de bloques
        cursor.execute("SELECT COUNT(*) as total FROM blockchain")
        total = cursor.fetchone()['total']
        
        # Calcular offset
        offset = (page - 1) * limit
        
        # Obtener bloques
        cursor.execute("""
            SELECT *
            FROM blockchain
            ORDER BY indice DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        bloques = cursor.fetchall()
        
        return {
            'bloques': bloques,
            'total_paginas': (total + limit - 1) // limit,
            'pagina_actual': page
        }
        
    except Exception as e:
        print(f"Error obteniendo últimos bloques: {str(e)}")
        return {'bloques': [], 'total_paginas': 0, 'pagina_actual': 1}
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def read_and_save():
    try:
        from app import app  # Importar Flask app después de ajustar el path
    except ImportError as e:
        print(f"❌ Error importando la aplicación Flask: {e}")
        return
    
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
        arduino = ArduinoConnection()
        if arduino.connect():
            print("📊 Leyendo y guardando datos (presiona Ctrl+C para detener)...")
        
        while arduino.is_connected:
            try:
                line = arduino.read_data()
                if line and line.startswith('Distance:'):
                    distancia = float(line.split(':')[1].split('cm')[0].strip())
                    if guardar_distancia(cursor, distancia, app):  # Pass app here
                        conn.commit()
                time.sleep(0.1)  # Reducir el delay a 0.1 segundos
            except Exception as e:
                print(f"❌ Error al procesar línea: {str(e)}")
                
    except KeyboardInterrupt:
        print("\n⚠️ Lectura interrumpida por el usuario")
    except mysql.connector.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
    finally:
        print("\nCerrando conexiones...")
        arduino.disconnect()
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("✅ Conexión a base de datos cerrada")

if __name__ == "__main__":
    read_and_save()