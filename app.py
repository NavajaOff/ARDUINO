from flask import Flask, render_template
from src.Controller.arduino_controller import ArduinoController
from src.Model.arduino_model import ArduinoModel
from src.config.conexion import config_mysql

app = Flask(__name__)

# Inicialización del modelo y controlador
arduino_model = ArduinoModel(config_mysql)
arduino_controller = ArduinoController(arduino_model)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    return arduino_controller.get_stats()

@app.route('/api/trafico_por_hora')
def get_trafico_por_hora():
    return arduino_controller.get_trafico_por_hora()

@app.route('/api/verificar_integridad')
def api_verificar_integridad():
    return arduino_controller.verificar_integridad()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)