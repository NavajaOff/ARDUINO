# Este archivo debe agregarse en tu aplicación Flask (en el servidor EC2)
# Ubicación sugerida: src/Controller/api_controller.py

from flask import Blueprint, request, jsonify
import mysql.connector
from src.config.conexion import config_mysql_aws
from src.arduino.read_and_save import guardar_distancia, calcular_hash
from datetime import datetime
import time

api_arduino = Blueprint('api_arduino', __name__)

@api_arduino.route('/api/arduino-data', methods=['POST'])
def receive_arduino_data():
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400
    
    data = request.json
    
    try:
        conn = mysql.connector.connect(**config_mysql_aws)
        cursor = conn.cursor()
        
        distancia = float(data['distancia'])
        timestamp = data.get('timestamp', int(time.time() * 1000))
        fecha_hora = datetime.fromtimestamp(timestamp/1000)
        
        # Insert data
        sql = """INSERT INTO distancias (fecha_hora, distancia, hash, timestamp) 
                VALUES (%s, %s, %s, %s)"""
        datos = (fecha_hora, distancia, calcular_hash(data), timestamp)
        cursor.execute(sql, datos)
        conn.commit()
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Función para registrar las rutas del API
def register_api_routes(app):
    app.register_blueprint(api_arduino)
    print("✅ API Arduino registrada correctamente")

def init_database():
    try:
        conn = mysql.connector.connect(**config_mysql_aws)
        cursor = conn.cursor()
        
        # Add timestamp column to distancias table if it doesn't exist
        cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'distancias' 
        AND column_name = 'timestamp'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            ALTER TABLE distancias 
            ADD COLUMN timestamp BIGINT AFTER hash
            """)
            print("✅ Column 'timestamp' added to table 'distancias'")
        
        conn.commit()
        print("✅ Database updated successfully")
            
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Connection closed")

if __name__ == "__main__":
    init_database()