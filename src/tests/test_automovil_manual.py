from src.Model.automovil_model import Automovil
from src.Controller.automovil_controller import AutomovilController

print("--- PRUEBA MANUAL CRUD AUTOMOVIL ---\n")

# Crear un automóvil usando el controlador
print("Crear automóvil...")
resultado = AutomovilController.crear_automovil(placa="XYZ987", saldo=150.0)
print("Resultado creación:", resultado)

# Consultar por placa
print("\nConsultar por placa...")
consulta = AutomovilController.obtener_automovil_por_placa("XYZ987")
print("Resultado consulta:", consulta)

# Consultar por id
print("\nConsultar por id...")
if resultado:
    consulta_id = AutomovilController.obtener_automovil_por_id(resultado["id"])
    print("Resultado consulta por id:", consulta_id)
else:
    print("No se pudo consultar por id porque no se creó el automóvil.")

# Actualizar saldo
print("\nActualizar saldo...")
if resultado:
    actualizado = AutomovilController.actualizar_automovil(resultado["id"], saldo=300.0)
    print("Resultado actualización:", actualizado)
else:
    print("No se pudo actualizar porque no se creó el automóvil.")

# Eliminar automóvil
print("\nEliminar automóvil...")
if resultado:
    eliminado = AutomovilController.eliminar_automovil(resultado["id"])
    print("Resultado eliminación:", eliminado)
else:
    print("No se pudo eliminar porque no se creó el automóvil.")

# Vista simulada: mostrar datos en formato HTML
print("\n--- Vista simulada (HTML) ---")
if consulta:
    html = f"""
    <html>
        <head><title>Automóvil</title></head>
        <body>
            <h1>Datos del Automóvil</h1>
            <ul>
                <li>ID: {consulta['id']}</li>
                <li>Placa: {consulta['placa']}</li>
                <li>Saldo: {consulta['saldo']}</li>
            </ul>
        </body>
    </html>
    """
    print(html)
else:
    print("No hay datos para mostrar en la vista.")
