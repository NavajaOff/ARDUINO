from datetime import datetime, timedelta
import mysql.connector
import hashlib
import json

class ArduinoModel:
    def __init__(self, config_mysql):
        self.config_mysql = config_mysql

    def get_db_connection(self):
        return mysql.connector.connect(**self.config_mysql)

    def get_stats(self):
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
            
            # Registros de las últimas 24 horas
            cursor.execute(
                "SELECT COUNT(*) as total FROM registros_peaje WHERE fecha_hora >= %s",
                (datetime.now() - timedelta(days=1),)
            )
            registros_24h = cursor.fetchone()['total']
            
            # Verificación de integridad
            integridad_correcta = self.verificar_integridad(cursor)
            
            return {
                'total_registros': total_registros,
                'total_bloques': total_bloques,
                'ultimo_registro': ultimo_registro,
                'registros_24h': registros_24h,
                'integridad': integridad_correcta
            }
        finally:
            cursor.close()
            conn.close()

    def get_trafico_por_hora(self):
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
        except:
            return False

    @staticmethod
    def calcular_hash_bloque(bloque):
        bloque_string = str(bloque['indice']) + str(bloque['timestamp']) + str(bloque['datos']) + str(bloque['hash_anterior']) + str(bloque['nonce'])
        return hashlib.sha256(bloque_string.encode()).hexdigest()