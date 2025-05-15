from flask import Flask, jsonify, render_template, request
from src.Model.arduino_model import ArduinoModel
from src.arduino.read_and_save import ArduinoConnection

app = Flask(__name__)

class ArduinoController:
    def __init__(self, model: ArduinoModel):
        self.model = model
        self.arduino = ArduinoConnection()
        
    def get_stats(self):
        try:
            stats = self.model.get_stats()
            return jsonify(stats)
        except Exception as err:
            return jsonify({'error': str(err)}), 500

    def get_trafico_por_hora(self):
        try:
            trafico = self.model.get_trafico_por_hora()
            return jsonify(trafico)
        except Exception as err:
            return jsonify({'error': str(err)}), 500

    def verificar_integridad(self):
        try:
            conn = self.model.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            integridad_ok = self.model.verificar_integridad(cursor)
            
            return jsonify({
                'integridad_ok': integridad_ok,
                'mensaje': "La blockchain es válida" if integridad_ok else "Se detectaron problemas de integridad"
            })
        except Exception as err:
            return jsonify({'error': str(err)}), 500
        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()

    def get_datos_arduino(self):
        self.arduino.connect()  # Intentará conectar solo si no está conectado
        return self.arduino.read_data()

    def get_datos_tiempo_real(self):
        """Controller method for real-time data"""
        try:
            data = self.model.get_datos_tiempo_real()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

