
import mysql.connector
from src.config.conexion import config_mysql

class Automovil:
	def __init__(self, id=None, placa=None, saldo=0.0):
		self.id = id
		self.placa = placa
		self.saldo = saldo

	@staticmethod
	def obtener_por_id(id):
		conn = mysql.connector.connect(**config_mysql)
		cursor = conn.cursor(dictionary=True)
		cursor.execute("SELECT * FROM automovil WHERE id = %s", (id,))
		row = cursor.fetchone()
		cursor.close()
		conn.close()
		if row:
			return Automovil(row['id'], row['placa'], row['saldo'])
		return None

	@staticmethod
	def obtener_por_placa(placa):
		conn = mysql.connector.connect(**config_mysql)
		cursor = conn.cursor(dictionary=True)
		cursor.execute("SELECT * FROM automovil WHERE placa = %s", (placa,))
		row = cursor.fetchone()
		cursor.close()
		conn.close()
		if row:
			return Automovil(row['id'], row['placa'], row['saldo'])
		return None

	def guardar(self):
		conn = mysql.connector.connect(**config_mysql)
		cursor = conn.cursor()
		if self.id is None:
			cursor.execute(
				"INSERT INTO automovil (placa, saldo) VALUES (%s, %s)",
				(self.placa, self.saldo)
			)
			self.id = cursor.lastrowid
		else:
			cursor.execute(
				"UPDATE automovil SET placa=%s, saldo=%s WHERE id=%s",
				(self.placa, self.saldo, self.id)
			)
		conn.commit()
		cursor.close()
		conn.close()

	def eliminar(self):
		if self.id is not None:
			conn = mysql.connector.connect(**config_mysql)
			cursor = conn.cursor()
			cursor.execute("DELETE FROM automovil WHERE id=%s", (self.id,))
			conn.commit()
			cursor.close()
			conn.close()
			self.id = None
