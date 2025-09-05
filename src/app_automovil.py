import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from flask import Flask, render_template, request, redirect, url_for
from Controller.automovil_controller import AutomovilController

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'View', 'Templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return redirect(url_for('listar_automoviles'))

@app.route('/automoviles', methods=['GET', 'POST'])
def listar_automoviles():
    automoviles = AutomovilController.obtener_todos()
    mensaje = ""
    
    if request.method == 'POST':
        criterio = request.form.get('criterio')  # 'id' o 'placa'
        valor = request.form.get('valor')
        if criterio == 'id':
            try:
                automovil = AutomovilController.obtener_automovil_por_id(int(valor))
                automoviles = [automovil] if automovil else []
            except ValueError:
                automoviles = []
                mensaje = "ID debe ser un número."
        elif criterio == 'placa':
            automovil = AutomovilController.obtener_automovil_por_placa(valor)
            automoviles = [automovil] if automovil else []
        if not automoviles and not mensaje:
            mensaje = "No se encontró ningún vehículo con ese valor."
    
    return render_template('automovil.html', automoviles=automoviles, mensaje=mensaje)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_automovil():
    if request.method == 'POST':
        placa = request.form.get('placa')
        saldo = request.form.get('saldo', 0)
        AutomovilController.crear_automovil(placa, float(saldo))
        return redirect(url_for('listar_automoviles'))
    return render_template('agregar_vehiculo.html')

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar_automovil(id):
    automovil = AutomovilController.obtener_automovil_por_id(id)
    if request.method == 'POST':
        placa = request.form.get('placa')
        saldo = request.form.get('saldo', 0)
        AutomovilController.actualizar_automovil(id, placa, float(saldo))
        return redirect(url_for('listar_automoviles'))
    return render_template('actualizar_vehiculo.html', automovil=automovil)

@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_automovil(id):
    if request.method == 'POST':
        AutomovilController.eliminar_automovil(id)
        return redirect(url_for('listar_automoviles'))
    automovil = AutomovilController.obtener_automovil_por_id(id)
    return render_template('eliminar_vehiculo.html', automovil=automovil)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar_automovil():
    automovil = None
    mensaje = ""
    if request.method == 'POST':
        criterio = request.form.get('criterio')  # 'id' o 'placa'
        valor = request.form.get('valor')
        if criterio == 'id':
            try:
                automovil = AutomovilController.obtener_automovil_por_id(int(valor))
            except ValueError:
                mensaje = "ID debe ser un número."
        elif criterio == 'placa':
            automovil = AutomovilController.obtener_automovil_por_placa(valor)

        if not automovil and not mensaje:
            mensaje = "No se encontró ningún vehículo con ese valor."
    return render_template('buscar_vehiculo.html', automovil=automovil, mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)