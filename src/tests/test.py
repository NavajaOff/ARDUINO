import mysql.connector
import sys
import os

# Añadir el directorio padre al path para poder importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.conexion import config_mysql

def test_conexion_bd():
    try:
        # Intentar establecer conexión
        print("Intentando conectar a la base de datos...")
        conn = mysql.connector.connect(**config_mysql)
        
        if conn.is_connected():
            print("¡Conexión exitosa!")
            
            # Obtener información del servidor
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Versión del servidor MySQL: {version[0]}")
            
            # Verificar si existe la base de datos
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            print("\nTablas encontradas:")
            for tabla in tablas:
                print(f"- {tabla[0]}")
                
            return True
            
    except mysql.connector.Error as err:
        print(f"\nError de conexión: {err}")
        print("\nVerifica que:")
        print("1. El servidor MySQL esté corriendo")
        print("2. Las credenciales sean correctas")
        print("3. La base de datos 'arduino_peaje' exista")
        return False
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    test_conexion_bd()