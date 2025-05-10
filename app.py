from flask import Flask, render_template, jsonify, request
import mysql.connector
import json
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

# Configuración de la conexión MySQL
config_mysql = {
    'user': 'usuario',
    'password': 'contraseña',
    'host': 'localhost',
    'database': 'peaje_arduino',
    'raise_on_warnings': True
}

# Función para obtener conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(**config_mysql)

# Ruta principal - Dashboard
@app.route('/')
def index():
    return render_template('index.html')

# API para obtener las estadísticas generales
@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        integridad_correcta = verificar_integridad(cursor)
        
        return jsonify({
            'total_registros': total_registros,
            'total_bloques': total_bloques,
            'ultimo_registro': ultimo_registro,
            'registros_24h': registros_24h,
            'integridad': integridad_correcta
        })
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# API para obtener datos del tráfico por hora
@app.route('/api/trafico_por_hora')
def get_trafico_por_hora():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener tráfico de las últimas 24 horas agrupado por hora
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
        
        # Asegurar que tenemos datos para todas las horas
        horas_completas = []
        hora_actual = datetime.now().hour
        
        for i in range(24):
            hora = (hora_actual - 23 + i) % 24
            
            # Buscar si tenemos datos para esta hora
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
        
        return jsonify(horas_completas)
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# API para obtener los últimos bloques
@app.route('/api/bloques')
def get_bloques():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        offset = (page - 1) * limit
        
        # Obtener bloques con paginación
        cursor.execute("""
            SELECT * FROM blockchain 
            ORDER BY indice DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        bloques = cursor.fetchall()
        
        # Formatear datos para mejor visualización
        for bloque in bloques:
            # Convertir timestamp a fecha legible
            bloque['fecha'] = datetime.fromtimestamp(bloque['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            # Parsear datos JSON
            if isinstance(bloque['datos'], str):
                try:
                    bloque['datos'] = json.loads(bloque['datos'])
                except:
                    pass  # Mantener como string si no es JSON válido
        
        # Contar total de bloques para paginación
        cursor.execute("SELECT COUNT(*) as total FROM blockchain")
        total = cursor.fetchone()['total']
        
        return jsonify({
            'bloques': bloques,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        })
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# API para obtener detalles de un bloque específico
@app.route('/api/bloque/<int:indice>')
def get_bloque(indice):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el bloque
        cursor.execute("SELECT * FROM blockchain WHERE indice = %s", (indice,))
        bloque = cursor.fetchone()
        
        if not bloque:
            return jsonify({'error': 'Bloque no encontrado'}), 404
        
        # Formatear datos
        bloque['fecha'] = datetime.fromtimestamp(bloque['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Parsear datos JSON
        if isinstance(bloque['datos'], str):
            try:
                bloque['datos'] = json.loads(bloque['datos'])
            except:
                pass
        
        # Obtener registros asociados con este bloque
        cursor.execute("SELECT * FROM registros_peaje WHERE hash_bloque = %s", (bloque['hash'],))
        registros = cursor.fetchall()
        
        # Verificar integridad del bloque
        es_valido = verificar_bloque(bloque, cursor)
        
        return jsonify({
            'bloque': bloque,
            'registros': registros,
            'es_valido': es_valido
        })
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Función para verificar la integridad de la blockchain
def verificar_integridad(cursor):
    try:
        # Obtener todos los bloques ordenados por índice
        cursor.execute("SELECT * FROM blockchain ORDER BY indice")
        bloques = cursor.fetchall()
        
        if not bloques:
            return True  # No hay bloques, considerado válido
        
        # Verificar cada bloque
        for i in range(len(bloques)):
            bloque = bloques[i]
            
            # Verificar hash del bloque
            hash_calculado = calcular_hash_bloque(bloque)
            if hash_calculado != bloque['hash']:
                return False
            
            # Verificar enlace con bloque anterior (excepto para el bloque génesis)
            if i > 0 and bloque['hash_anterior'] != bloques[i-1]['hash']:
                return False
        
        return True
    except:
        return False

# Verificar un solo bloque
def verificar_bloque(bloque, cursor):
    try:
        hash_calculado = calcular_hash_bloque(bloque)
        
        # Verificar hash del propio bloque
        if hash_calculado != bloque['hash']:
            return False
        
        # Si no es el bloque génesis, verificar el enlace con el anterior
        if bloque['indice'] > 0:
            cursor.execute("SELECT hash FROM blockchain WHERE indice = %s", (bloque['indice'] - 1,))
            hash_anterior = cursor.fetchone()['hash']
            if bloque['hash_anterior'] != hash_anterior:
                return False
        
        return True
    except:
        return False

# Calcular hash de un bloque
def calcular_hash_bloque(bloque):
    bloque_string = str(bloque['indice']) + str(bloque['timestamp']) + str(bloque['datos']) + str(bloque['hash_anterior']) + str(bloque['nonce'])
    return hashlib.sha256(bloque_string.encode()).hexdigest()

# Ruta para verificar la integridad de toda la cadena
@app.route('/api/verificar_integridad')
def api_verificar_integridad():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        integridad_ok = verificar_integridad(cursor)
        
        return jsonify({
            'integridad_ok': integridad_ok,
            'mensaje': "La blockchain es válida" if integridad_ok else "Se detectaron problemas de integridad"
        })
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Ruta para obtener estadísticas por día
@app.route('/api/estadisticas_diarias')
def get_estadisticas_diarias():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estadísticas de los últimos 7 días
        cursor.execute("""
            SELECT 
                DATE(fecha_hora) as fecha,
                COUNT(*) as cantidad,
                MIN(fecha_hora) as primera_deteccion,
                MAX(fecha_hora) as ultima_deteccion
            FROM 
                registros_peaje
            WHERE 
                fecha_hora >= %s
            GROUP BY 
                DATE(fecha_hora)
            ORDER BY 
                fecha DESC
        """, (datetime.now() - timedelta(days=7),))
        
        estadisticas = cursor.fetchall()
        
        return jsonify(estadisticas)
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)