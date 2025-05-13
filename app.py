from flask import Flask, render_template, jsonify
from src.Controller.arduino_controller import ArduinoController
from src.Model.arduino_model import ArduinoModel
from src.config.conexion import config_mysql

app = Flask(__name__, 
           template_folder='src/View/Templates',
           static_folder='src/View/Static')

# Inicialización del modelo y controlador
arduino_model = ArduinoModel(config_mysql)
arduino_controller = ArduinoController(arduino_model)

@app.route('/')
def index():
    try:
        # Obtener datos iniciales
        stats = arduino_model.get_stats()
        trafico = arduino_model.get_trafico_por_hora()
        estadisticas_diarias = arduino_model.get_estadisticas_diarias()
        ultimos_bloques = arduino_model.get_ultimos_bloques()

        # Pasar datos al template
        return render_template('index.html',
                            stats=stats,
                            trafico_por_hora=trafico,
                            estadisticas_diarias=estadisticas_diarias,
                            ultimos_bloques=ultimos_bloques,
                            error=None)
    except Exception as e:
        return render_template('index.html', 
                             error=str(e))

@app.route('/api/stats')
def get_stats():
    return arduino_controller.get_stats()

@app.route('/api/trafico_por_hora')
def get_trafico_por_hora():
    return arduino_controller.get_trafico_por_hora()

@app.route('/api/verificar_integridad')
def api_verificar_integridad():
    return arduino_controller.verificar_integridad()

@app.route('/api/datos_tiempo_real')
def datos_tiempo_real():
    try:
        # Obtener último registro
        ultimo_registro = arduino_model.get_ultimo_registro()
        return jsonify(ultimo_registro)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)