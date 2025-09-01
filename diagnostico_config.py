#!/usr/bin/env python3
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, 'src')

# Determinar qué configuración usar basado en el entorno
print(f"Variable ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")

if os.environ.get('ENVIRONMENT') == 'production':
    from src.config.conexion_aws import config_mysql_aws as db_config
    print("✅ Usando configuración AWS (production)")
else:
    try:
        from src.config.conexion_local import config_mysql_local as db_config
        print("⚠️  Usando configuración LOCAL (desarrollo)")
    except ImportError:
        from src.config.conexion_aws import config_mysql_aws as db_config
        print("✅ Usando configuración AWS (fallback)")

print(f"Configuración actual: {db_config}")

# Probar conexión
try:
    import mysql.connector
    conn = mysql.connector.connect(**db_config)
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")
