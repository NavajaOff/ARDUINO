import mysql.connector
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config.conexion import config_mysql_aws

def init_database():
    try:
        conn = mysql.connector.connect(**config_mysql_aws)
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
                hash VARCHAR(64),
                timestamp BIGINT
            )
            ''')
            
            conn.commit()
            print("✅ Tabla distancias creada correctamente")
        else:
            print("ℹ️ La tabla distancias ya existe")

        # Crear tabla registros_peaje
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros_peaje (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha_hora DATETIME,
            estado VARCHAR(50),
            hash VARCHAR(64)
        )
        ''')
        
        # Crear tabla blockchain
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            indice INT PRIMARY KEY,
            timestamp DATETIME,
            datos TEXT,
            hash VARCHAR(64),
            hash_anterior VARCHAR(64),
            nonce INT
        )
        ''')
        
        conn.commit()
        print("✅ Tablas creadas correctamente")

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