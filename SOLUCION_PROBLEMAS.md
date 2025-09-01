# Solución a Problemas Reportados

## 1. Error de Base de Datos Local

**Problema:** `Access denied for user 'arduino_user'@'localhost' (using password: YES)`

**Solución:**

### Opción A: Crear el usuario en MySQL local
```sql
-- Conectarse a MySQL como root
mysql -u root -p

-- Crear la base de datos
CREATE DATABASE arduino_peaje;

-- Crear el usuario
CREATE USER 'arduino_user'@'localhost' IDENTIFIED BY 'Arduino123!';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON arduino_peaje.* TO 'arduino_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;
```

### Opción B: Usar configuración local alternativa (Recomendado)
He creado un archivo `src/config/conexion_local.py` con credenciales por defecto de MySQL. El sistema ahora:

1. Usa configuración local si existe
2. Si no, usa la configuración de AWS
3. Puedes modificar `src/config/conexion_local.py` con tus credenciales reales

### Opción C: Configurar variable de entorno
```bash
# En Windows (CMD)
set ENVIRONMENT=production

# En Windows (PowerShell)
$env:ENVIRONMENT="production"

# En Linux/Mac
export ENVIRONMENT=production
```

## 2. Error de Puerto en AWS

**Problema:** `Port 5000 is in use by another program`

**Solución:**

### Opción A: Encontrar y detener el proceso
```bash
# Encontrar qué proceso usa el puerto 5000
netstat -ano | findstr :5000

# Matar el proceso (reemplaza PID con el número real)
taskkill /PID numero-puerto /F

```

### Opción B: Usar un puerto diferente
```bash
# Cambiar el puerto en app.py al final del archivo:
app.run(debug=True, host='0.0.0.0', port=5001)

# O ejecutar con puerto diferente:
python3 app.py --port 5001
```

### Opción C: Usar el comando correcto en AWS
```bash
# En lugar de:
python3 app.py

# Usar:
python3 app.py runserver --port 5001
# o
flask run --port 5001
```

## Configuración Recomendada

### Para Desarrollo Local:
1. Asegúrate de que MySQL esté instalado y ejecutándose
2. Modifica `src/config/conexion_local.py` con tus credenciales reales
3. Ejecuta: `python app.py runserver`

### Para Producción (AWS):
1. Configura la variable de entorno: `export ENVIRONMENT=production`
2. Asegúrate de que MySQL esté configurado correctamente
3. Usa un puerto disponible: `python3 app.py --port 5001`

## Verificación de Configuración

Para verificar que la configuración es correcta:

```python
# Prueba de conexión simple
import mysql.connector
from src.config.conexion_local import config_mysql_local

try:
    conn = mysql.connector.connect(**config_mysql_local)
    print("✅ Conexión exitosa a MySQL local")
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

## Notas Importantes

1. **MySQL debe estar instalado y ejecutándose** en tu máquina local
2. **Las tablas se crean automáticamente** al ejecutar la aplicación por primera vez
3. **El puerto 5000** es comúnmente usado por otros servicios, prueba con 5001, 8000, etc.
4. **En AWS**, asegúrate de que los security groups permitan el tráfico en el puerto elegido
