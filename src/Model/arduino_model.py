import mysql.connector
from datetime import datetime, timedelta
import hashlib
import json

class ArduinoModel:
    def __init__(self, config):
        self.config = config

    def get_db_connection(self):
        return mysql.connector.connect(**self.config)

    def get_total_registros(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM registros_peaje")
            total = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return total
        except Exception as e:
            print(f"Error al obtener total de registros: {e}")
            return 0

    def get_stats(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                # Total de registros
                cursor.execute("SELECT COUNT(*) as total FROM registros_peaje")
                total_registros = cursor.fetchone()['total']
                
                # Total de bloques
                cursor.execute("SELECT COUNT(*) as total FROM blockchain")
                total_bloques = cursor.fetchone()['total']
                
                # Último registro
                cursor.execute("SELECT * FROM registros_peaje ORDER BY id DESC LIMIT 1")
                ultimo_registro = cursor.fetchone()
                
                if ultimo_registro:
                    ultimo_registro['fecha_hora'] = ultimo_registro['fecha_hora'].isoformat()
                
                # Registros de las últimas 24 horas
                cursor.execute(
                    "SELECT COUNT(*) as total FROM registros_peaje WHERE fecha_hora >= %s",
                    (datetime.now() - timedelta(days=1),)
                )
                registros_24h = cursor.fetchone()['total']
                
                # Verificación de integridad
                integridad_correcta = self.verificar_integridad(cursor)
                
                stats = {
                    'total_registros': total_registros,
                    'total_bloques': total_bloques,
                    'ultimo_registro': ultimo_registro,
                    'registros_24h': registros_24h,
                    'integridad': integridad_correcta
                }
                return stats
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'error': str(e)}

    def get_trafico_por_hora(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT 
                        HOUR(fecha_hora) as hora,
                        COUNT(*) as cantidad
                    FROM 
                        registros_peaje
                    WHERE 
                        fecha_hora >= %s
                    GROUP BY 
                        HOUR(fecha_hora)
                    ORDER BY 
                        hora
                """, (datetime.now() - timedelta(days=1),))
                
                trafico_por_hora = cursor.fetchall()
                return self._completar_horas(trafico_por_hora)
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting traffic per hour: {e}")
            return []

    def _completar_horas(self, trafico_por_hora):
        horas_completas = []
        hora_actual = datetime.now().hour
        
        for i in range(24):
            hora = (hora_actual - 23 + i) % 24
            encontrado = False
            for registro in trafico_por_hora:
                if registro['hora'] == hora:
                    horas_completas.append({
                        'hora': hora,
                        'cantidad': registro['cantidad']
                    })
                    encontrado = True
                    break
            
            if not encontrado:
                horas_completas.append({
                    'hora': hora,
                    'cantidad': 0
                })
        return horas_completas

    def verificar_integridad(self, cursor):
        try:
            cursor.execute("SELECT * FROM blockchain ORDER BY indice")
            bloques = cursor.fetchall()
            
            if not bloques:
                return True
            
            for i in range(len(bloques)):
                bloque = bloques[i]
                hash_calculado = self.calcular_hash_bloque(bloque)
                if hash_calculado != bloque['hash']:
                    return False
                if i > 0 and bloque['hash_anterior'] != bloques[i-1]['hash']:
                    return False
            return True
        except Exception as e:
            print(f"Error verifying integrity: {e}")
            return False

    @staticmethod
    def calcular_hash_bloque(bloque):
        # Crear un diccionario con el mismo formato que al crear el bloque
        bloque_dict = {
            'indice': bloque['indice'],
            'timestamp': bloque['timestamp'],
            'datos': bloque['datos'],
            'hash_anterior': bloque['hash_anterior'],
            'nonce': bloque['nonce']
        }
        # Usar str() para convertir el diccionario completo
        return hashlib.sha256(str(bloque_dict).encode()).hexdigest()

    def get_estadisticas_diarias(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT DATE(fecha_hora) as fecha, COUNT(*) as total 
                    FROM registros_peaje 
                    GROUP BY DATE(fecha_hora) 
                    ORDER BY fecha DESC 
                    LIMIT 7
                """)
                result = cursor.fetchall()
                # Convert date objects to ISO format strings
                for row in result:
                    row['fecha'] = row['fecha'].isoformat()
                return result
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error al obtener estadísticas diarias: {e}")
            return []

    def get_ultimos_bloques(self, pagina=1, por_pagina=10):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                # Obtener total de bloques
                cursor.execute("SELECT COUNT(*) as total FROM blockchain")
                total = cursor.fetchone()['total']
                
                # Calcular offset
                offset = (pagina - 1) * por_pagina
                
                # Obtener bloques para la página actual
                cursor.execute("""
                    SELECT * FROM blockchain 
                    ORDER BY indice DESC 
                    LIMIT %s OFFSET %s
                """, (por_pagina, offset))
                
                bloques = cursor.fetchall()
                
                return {
                    'bloques': bloques,
                    'total_paginas': (total + por_pagina - 1) // por_pagina,
                    'pagina_actual': pagina
                }
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting latest blocks: {e}")
            return {'error': str(e)}

    def get_bloque_detalle(self, indice):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                # Obtener bloque
                cursor.execute("SELECT * FROM blockchain WHERE indice = %s", (indice,))
                bloque = cursor.fetchone()
                
                if bloque:
                    # Obtener registros asociados al bloque
                    datos = json.loads(bloque['datos'])
                    ids_registros = [reg['id'] for reg in datos['registros']]
                    
                    if ids_registros:
                        cursor.execute("""
                            SELECT id, fecha_hora, hash 
                            FROM registros_peaje 
                            WHERE id IN ({})
                        """.format(','.join(['%s'] * len(ids_registros))), 
                        tuple(ids_registros))
                        
                        registros = cursor.fetchall()
                        bloque['registros'] = registros
                    
                    return bloque
                return None
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting block details: {e}")
            return None

    def get_ultimo_registro(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT r.*, d.distancia 
                    FROM registros_peaje r 
                    LEFT JOIN distancias d ON r.hash = d.hash 
                    ORDER BY r.id DESC 
                    LIMIT 1
                """)
                return cursor.fetchone()
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting last record: {e}")
            return None

    def get_datos_tiempo_real(self):
        """Get real-time data from the most recent vehicle detection"""
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            try:
                # Get latest record
                cursor.execute("""
                    SELECT 
                        r.id,
                        r.fecha_hora,
                        r.hash,
                        r.estado,
                        d.distancia,
                        (SELECT COUNT(*) FROM registros_peaje) as total_registros
                    FROM registros_peaje r
                    LEFT JOIN distancias d ON r.fecha_hora = d.fecha_hora
                    ORDER BY r.fecha_hora DESC
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                
                if result:
                    # Convert datetime to string for JSON serialization
                    result['fecha_hora'] = result['fecha_hora'].isoformat()
                    return result
                
                return {
                    'id': None,
                    'fecha_hora': None,
                    'hash': None,
                    'estado': None,
                    'distancia': None,
                    'total_registros': 0
                }
            finally:
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            raise Exception(f"Error de base de datos: {err}")

    def save_reading(self, timestamp, distancia):
        """Saves a new reading in distancias, registros_peaje, and blockchain if needed"""
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            fecha_hora = datetime.fromtimestamp(timestamp/1000)
            estado = "VEHICULO DETECTADO"
            # Datos para hash
            datos_peaje = {
                'fecha_hora': fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
                'estado': estado,
                'distancia': distancia
            }
            hash_registro = hashlib.sha256(json.dumps(datos_peaje).encode()).hexdigest()

            # Insertar en distancias
            cursor.execute(
                "INSERT INTO distancias (fecha_hora, distancia, hash, timestamp) VALUES (%s, %s, %s, %s)",
                (fecha_hora, distancia, hash_registro, timestamp)
            )

            # Insertar en registros_peaje
            cursor.execute(
                "INSERT INTO registros_peaje (fecha_hora, estado, hash) VALUES (%s, %s, %s)",
                (fecha_hora, estado, hash_registro)
            )

            # Verificar si se debe crear un nuevo bloque
            cursor.execute("SELECT id, fecha_hora, estado, hash FROM registros_peaje WHERE bloque_id IS NULL ORDER BY id LIMIT 5")
            registros_sin_bloque = cursor.fetchall()

            if len(registros_sin_bloque) == 5:
                # Obtener último bloque
                cursor.execute("SELECT * FROM blockchain ORDER BY indice DESC LIMIT 1")
                ultimo_bloque = cursor.fetchone()
                indice = 1 if not ultimo_bloque else ultimo_bloque[0] + 1
                timestamp_bloque = datetime.now().timestamp()
                datos_bloque = {
                    'registros': [
                        {
                            'id': reg[0],
                            'fecha_hora': reg[1].strftime('%Y-%m-%d %H:%M:%S'),
                            'estado': reg[2],
                            'hash': reg[3]
                        } for reg in registros_sin_bloque
                    ]
                }
                hash_anterior = '0' * 64 if not ultimo_bloque else ultimo_bloque[4]
                nonce = 0
                while True:
                    bloque = {
                        'indice': indice,
                        'timestamp': timestamp_bloque,
                        'datos': json.dumps(datos_bloque),
                        'hash_anterior': hash_anterior,
                        'nonce': nonce
                    }
                    hash_bloque = hashlib.sha256(str(bloque).encode()).hexdigest()
                    if hash_bloque.startswith('00'):
                        break
                    nonce += 1

                # Insertar nuevo bloque
                cursor.execute(
                    "INSERT INTO blockchain (indice, timestamp, datos, hash_anterior, hash, nonce) VALUES (%s, %s, %s, %s, %s, %s)",
                    (indice, timestamp_bloque, json.dumps(datos_bloque), hash_anterior, hash_bloque, nonce)
                )

                # Actualizar registros con el ID del bloque
                ids_registros = [reg[0] for reg in registros_sin_bloque]
                cursor.execute(
                    "UPDATE registros_peaje SET bloque_id = %s WHERE id IN ({})".format(','.join(['%s'] * len(ids_registros))),
                    [indice] + ids_registros
                )

            conn.commit()
            print(f"✅ Reading saved and processed: {distancia}cm at {fecha_hora}")
            return True

        except mysql.connector.Error as err:
            print(f"❌ Database error: {err}")
            raise Exception(f"Database error: {err}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()