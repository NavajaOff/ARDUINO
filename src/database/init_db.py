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
        
        # Verificar si las tablas existen
        cursor.execute("SHOW TABLES")
        tablas_existentes = [table[0] for table in cursor.fetchall()]
        
        if 'registros_peaje' in tablas_existentes and 'blockchain' in tablas_existentes:
            print("ℹ️ Las tablas ya existen en la base de datos")
        else:
            # Crear tabla registros_peaje si no existe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_peaje (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha_hora DATETIME,
                hash VARCHAR(64),
                bloque_id INT NULL
            )
            ''')
            
            # Crear tabla blockchain si no existe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain (
                indice INT PRIMARY KEY,
                timestamp DOUBLE,
                datos TEXT,
                hash_anterior VARCHAR(64),
                hash VARCHAR(64),
                nonce INT
            )
            ''')
            
            conn.commit()
            print("✅ Tablas creadas correctamente")

        # Mostrar estructura de las tablas
        print("\nEstructura de las tablas:")
        for tabla in ['registros_peaje', 'blockchain']:
            print(f"\n📋 Tabla: {tabla}")
            cursor.execute(f"DESCRIBE {tabla}")
            for columna in cursor.fetchall():
                print(f"  - {columna[0]}: {columna[1]}")
            
            # Mostrar número de registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"  Registros totales: {count}")
            
    except mysql.connector.Error as err:
        print(f"❌ Error al inicializar la base de datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    init_database()