import mysql.connector
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config.conexion import config_mysql

def init_database():
    try:
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        
        # Verificar si la tabla distancias existe
        cursor.execute("SHOW TABLES")
        tablas_existentes = [table[0] for table in cursor.fetchall()]
        
        if 'distancias' not in tablas_existentes:
            # Crear tabla distancias
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS distancias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha_hora DATETIME,
                distancia FLOAT,
                hash VARCHAR(64)
            )
            ''')
            
            conn.commit()
            print("✅ Tabla distancias creada correctamente")
        else:
            print("ℹ️ La tabla distancias ya existe")

        # Mostrar estructura de la tabla
        print("\n📋 Estructura de la tabla distancias:")
        cursor.execute("DESCRIBE distancias")
        for columna in cursor.fetchall():
            print(f"  - {columna[0]}: {columna[1]}")
        
        # Mostrar número de registros
        cursor.execute("SELECT COUNT(*) FROM distancias")
        count = cursor.fetchone()[0]
        print(f"\nRegistros totales en distancias: {count}")
            
    except mysql.connector.Error as err:
        print(f"❌ Error al inicializar la base de datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    init_database()