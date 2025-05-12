from flask import Flask
import mysql.connector

app = Flask(__name__)

def test_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="arduino_peaje"
        )
        if connection.is_connected():
            return "Conexión a MySQL exitosa!"
        else:
            return "No se pudo conectar a MySQL"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

@app.route('/')
def hello():
    mysql_status = test_mysql_connection()
    return f'Flask está instalado!<br>{mysql_status}'

if __name__ == '__main__':
    app.run(debug=True)