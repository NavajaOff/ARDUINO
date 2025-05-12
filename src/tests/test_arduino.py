import serial
import time
from serial.tools import list_ports

def test_arduino_connection():
    # Listar todos los puertos disponibles
    print("Puertos seriales disponibles:")
    ports = list_ports.comports()
    for port in ports:
        print(f"- {port.device}: {port.description}")
    
    try:
        # Intentar conectar al Arduino
        print("\nIntentando conectar al Arduino en COM3...")
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # Esperar a que se establezca la conexión
        
        print("¡Conexión establecida!")
        print("Escuchando datos del Arduino (presiona Ctrl+C para detener)...")
        
        # Leer datos durante 10 segundos
        timeout = time.time() + 10
        datos_recibidos = False
        
        while time.time() < timeout:
            if arduino.in_waiting:
                dato = arduino.readline().decode('utf-8').strip()
                print(f"Dato recibido: {dato}")
                datos_recibidos = True
            time.sleep(0.1)
        
        if not datos_recibidos:
            print("\n⚠️ No se recibieron datos en 10 segundos.")
            print("Verifica que el código arduino_code.ino esté cargado y funcionando.")
        
    except serial.SerialException as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\nVerifica que:")
        print("1. El Arduino esté conectado físicamente")
        print("2. El puerto COM3 sea el correcto")
        print("3. No haya otro programa usando el puerto (como el Monitor Serial de Arduino IDE)")
        return False
        
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    test_arduino_connection()