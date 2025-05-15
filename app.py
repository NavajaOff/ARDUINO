from flask import Flask, render_template, jsonify, make_response, Response, stream_with_context
from datetime import datetime
from src.Controller.arduino_controller import ArduinoController
from src.Model.arduino_model import ArduinoModel
from src.config.conexion import config_mysql
import json
import time

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

@app.route('/api/estadisticas_diarias')
def get_estadisticas_diarias():
    return jsonify(arduino_model.get_estadisticas_diarias())

@app.route('/api/ultimos_bloques')
def get_ultimos_bloques():
    return jsonify(arduino_model.get_ultimos_bloques())

@app.route('/api/datos_tiempo_real')
def datos_tiempo_real():
    """Get real-time data endpoint"""
    return arduino_controller.get_datos_tiempo_real()

@app.route('/events')
def events():
    def generate():
        while True:
            try:
                # Get the latest data
                data = {
                    'stats': arduino_model.get_stats(),
                    'trafico': arduino_model.get_trafico_por_hora(),
                    'estadisticas': arduino_model.get_estadisticas_diarias(),
                    'bloques': arduino_model.get_ultimos_bloques()
                }
                
                # Format the SSE data properly
                yield f"retry: 1000\ndata: {json.dumps(data)}\n\n"
                time.sleep(1)  # Esperar 1 segundo entre actualizaciones
            except Exception as e:
                print(f"Error generating SSE data: {e}")
                yield f"retry: 5000\ndata: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(5)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*',
            'Connection': 'keep-alive'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)