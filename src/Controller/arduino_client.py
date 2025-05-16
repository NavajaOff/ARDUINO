import serial
import requests
import time
import sys
from serial.tools import list_ports

# Configuración
ARDUINO_PORT = 'COM3'  # Cambia esto según tu puerto Arduino
BAUD_RATE = 9600
SERVER_URL = 'http://18.188.169.252:5000/api/arduino-data'  # URL de tu servidor EC2

class ArduinoClient:
    def __init__(self, port=ARDUINO_PORT, baud_rate=BAUD_RATE, server_url=SERVER_URL):
        self.port = port
        self.baud_rate = baud_rate
        self.server_url = server_url
        self.connection = None
        self.is_connected = False
        self.last_status = None

    def list_available_ports(self):
        """Lista todos los puertos seriales disponibles"""
        ports = list_ports.comports()
        print("Puertos disponibles:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device}: {port.description}")
        return ports

    def connect(self, port=None):
        """Conecta al Arduino en el puerto especificado"""
        if port:
            self.port = port
            
        try:
            if not self.is_connected:
                self.connection = serial.Serial(self.port, self.baud_rate)
                time.sleep(2)  # Esperar a que se establezca la conexión
                if self.connection.is_open:
                    self.is_connected = True
                    if self.last_status != "connected":
                        print(f"¡Conexión establecida en {self.port}!")
                        self.last_status = "connected"
                    return True
        except Exception as e:
            if self.last_status != "error":
                print(f"❌ Error de conexión: {e}")
                self.last_status = "error"
            self.is_connected = False
            return False

    def disconnect(self):
        """Cierra la conexión con el Arduino"""
        if self.connection and self.is_connected:
            self.connection.close()
            self.is_connected = False
            if self.last_status != "closed":
                print("Conexión cerrada.")
                self.last_status = "closed"

    def read_data(self):
        """Lee datos del Arduino si hay disponibles"""
        if self.is_connected and self.connection:
            try:
                if self.connection.in_waiting:
                    return self.connection.readline().decode('utf-8').strip()
            except Exception as e:
                print(f"❌ Error leyendo datos: {e}")
                self.disconnect()
                return None
        return None

    def send_to_server(self, distancia):
        """Envía los datos de distancia al servidor"""
        try:
            payload = {"distancia": distancia}
            response = requests.post(self.server_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Datos enviados: {distancia} cm - {data.get('message')}")
                    return True
                else:
                    print(f"ℹ️ {data.get('message')}")
                    return True
            else:
                print(f"❌ Error del servidor ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error enviando datos: {e}")
            return False

def main():
    client = ArduinoClient()
    
    # Listar puertos disponibles
    ports = client.list_available_ports()
    
    # Si hay más de un puerto, permitir seleccionar
    if len(ports) > 1:
        try:
            selection = int(input("\nSelecciona el número del puerto Arduino: "))
            if 1 <= selection <= len(ports):
                selected_port = ports[selection-1].device
                print(f"Puerto seleccionado: {selected_port}")
            else:
                print(f"Selección inválida. Usando puerto por defecto: {ARDUINO_PORT}")
                selected_port = ARDUINO_PORT
        except ValueError:
            print(f"Entrada inválida. Usando puerto por defecto: {ARDUINO_PORT}")
            selected_port = ARDUINO_PORT
    elif len(ports) == 1:
        selected_port = ports[0].device
        print(f"Un solo puerto encontrado, usando: {selected_port}")
    else:
        print(f"No se encontraron puertos. Intentando con el puerto por defecto: {ARDUINO_PORT}")
        selected_port = ARDUINO_PORT
    
    # Conectar al Arduino
    if not client.connect(selected_port):
        print("No se pudo conectar al Arduino. Verifique la conexión y el puerto.")
        return
    
    print(f"\n🔄 Enviando datos a {SERVER_URL}")
    print("Presiona Ctrl+C para detener...\n")
    
    try:
        while True:
            line = client.read_data()
            if line and line.startswith('Distance:'):
                try:
                    distancia = float(line.split(':')[1].split('cm')[0].strip())
                    client.send_to_server(distancia)
                except ValueError as e:
                    print(f"❌ Error procesando dato: {e} - Línea: {line}")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Programa detenido por el usuario")
    finally:
        client.disconnect()
        print("Programa finalizado.")

if __name__ == "__main__":
    main()