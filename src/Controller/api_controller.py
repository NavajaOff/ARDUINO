# Este archivo debe agregarse en tu aplicación Flask (en el servidor EC2)
# Ubicación sugerida: src/Controller/api_controller.py

from flask import Blueprint, request, jsonify
import mysql.connector
from src.config.conexion import config_mysql
from src.arduino.read_and_save import guardar_distancia, calcular_hash
from datetime import datetime

api_arduino = Blueprint('api_arduino', __name__)

@api_arduino.route('/api/arduino-data', methods=['POST'])
def receive_arduino_data():
    """
    Endpoint que recibe datos del Arduino desde un cliente remoto
    Espera un JSON con el formato: {"distancia": valor_float}
    """
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400
    
    data = request.json
    
    if 'distancia' not in data:
        return jsonify({"error": "El campo 'distancia' es requerido"}), 400
    
    try:
        distancia = float(data['distancia'])
        
        # Conectar a la base de datos
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        # Procesar los datos recibidos usando la función existente
        # Accedemos a la aplicación Flask actual
        from flask import current_app
        result = guardar_distancia(cursor, distancia, current_app._get_current_object())
        
        if result:
            conn.commit()
            response = {"success": True, "message": "Datos procesados correctamente"}
        else:
            response = {"success": True, "message": "Datos recibidos pero no generaron un nuevo registro"}
            
    except Exception as e:
        response = {"error": str(e)}
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    
    return jsonify(response)

# Función para registrar las rutas del API
def register_api_routes(app):
    app.register_blueprint(api_arduino)
    print("✅ API Arduino registrada correctamente")