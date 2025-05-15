from flask import Flask
from flask_sock import Sock
from datetime import datetime
import json

app = Flask(__name__)
sock = Sock(app)
connected_clients = set()

@sock.route('/ws')
def ws(sock):
    connected_clients.add(sock)
    try:
        while True:
            data = sock.receive()
            # Mantener la conexión viva
            if data == "ping":
                sock.send("pong")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(sock)

def broadcast_update(data):
    dead_clients = set()
    for client in connected_clients:
        try:
            client.send(json.dumps(data))
        except Exception:
            dead_clients.add(client)
    connected_clients.difference_update(dead_clients)

# Guardar la función broadcast en el contexto de la aplicación
app.broadcast = broadcast_update