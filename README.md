# Proyecto de Detección de Vehículos con Blockchain

Este proyecto implementa un sistema de detección de vehículos utilizando un microcontrolador Arduino y una blockchain en Python. El sistema registra la detección de vehículos y almacena los datos en una base de datos MySQL.

## Estructura del Proyecto

```
arduino_project
├── src
│   ├── conexion.py          # Implementación de la blockchain en Python
│   └── arduino
│       └── arduino_code.ino # Código de Arduino para la detección de vehículos
├── README.md                # Documentación del proyecto
```

## Requisitos

- Python 3.x
- Bibliotecas de Python: `mysql-connector-python`, `pyserial`
- Arduino IDE
- Sensor de detección de vehículos (por ejemplo, un sensor ultrasónico)

## Instrucciones de Configuración

### Configuración del Arduino

1. Abre el archivo `src/arduino/arduino_code.ino` en el Arduino IDE.
2. Conecta el sensor de detección de vehículos al Arduino según las especificaciones del sensor.
3. Carga el código en el microcontrolador.

### Configuración del Entorno Python

1. Asegúrate de tener Python 3.x instalado en tu sistema.
2. Instala las bibliotecas necesarias ejecutando:
   ```
   pip install mysql-connector-python pyserial
   ```
3. Configura la conexión a la base de datos MySQL en el archivo `src/conexion.py` modificando el diccionario `config_mysql` con tus credenciales.

### Ejecución del Proyecto

1. Inicia el servidor MySQL y asegúrate de que la base de datos `peaje_arduino` esté creada.
2. Ejecuta el script de Python:
   ```
   python src/conexion.py
   ```
3. El script se conectará al Arduino y comenzará a recibir datos de detección de vehículos.

## Funcionamiento

- El Arduino detecta la presencia de un vehículo utilizando el sensor y envía un mensaje a través del puerto serial en el formato `VEHICULO_DETECTADO,timestamp`.
- El script de Python recibe estos datos, los procesa y los almacena en la blockchain y en la base de datos MySQL.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.