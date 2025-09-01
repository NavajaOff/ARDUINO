
import mysql.connector
from src.config.conexion import config_mysql

class Automovil:
	def __init__(self, id=None, placa=None, saldo=0.0):
		self.id = id
		self.placa = placa
		self.saldo = saldo

	@staticmethod
	def obtener_por_id(id):
		conn = None
		cursor = None
		try:
			conn = mysql.connector.connect(**config_mysql)
			cursor = conn.cursor(dictionary=True)
			cursor.execute("SELECT * FROM automovil WHERE id = %s", (id,))
			row = cursor.fetchone()
			if row:
				return Automovil(row['id'], row['placa'], row['saldo'])
			return None
		except mysql.connector.Error as err:
			print(f"Error al obtener automovil por id: {err}")
			return None
		finally:
			if cursor:
				try:
					cursor.close()
				except Exception as e:
					print(f"Error al cerrar el cursor: {e}")
			if conn:
				try:
					conn.close()
				except Exception as e:
					print(f"Error al cerrar la conexión: {e}")

	@staticmethod
	def obtener_por_placa(placa):
		conn = None
		cursor = None
		try:
			conn = mysql.connector.connect(**config_mysql)
			cursor = conn.cursor(dictionary=True)
			cursor.execute("SELECT * FROM automovil WHERE placa = %s", (placa,))
			row = cursor.fetchone()
			if row:
				return Automovil(row['id'], row['placa'], row['saldo'])
			return None
		except mysql.connector.Error as err:
			print(f"Error al obtener automovil por placa: {err}")
			return None
		finally:
			if cursor:
				try:
					cursor.close()
				except Exception as e:
					print(f"Error al cerrar el cursor: {e}")
			if conn:
				try:
					conn.close()
				except Exception as e:
					print(f"Error al cerrar la conexión: {e}")

	def guardar(self):
		# Validación de datos
		if not self.placa or not isinstance(self.placa, str):
			print("Error: La placa no puede estar vacía y debe ser un string.")
			return
		if not isinstance(self.saldo, (int, float)) or self.saldo < 0:
			print("Error: El saldo debe ser un número mayor o igual a 0.")
			return
		conn = None
		cursor = None
		try:
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
		except mysql.connector.Error as err:
			print(f"Error al guardar automovil: {err}")
		finally:
			if cursor:
				try:
					cursor.close()
				except Exception as e:
					print(f"Error al cerrar el cursor: {e}")
			if conn:
				try:
					conn.close()
				except Exception as e:
					print(f"Error al cerrar la conexión: {e}")

	def eliminar(self):
		if self.id is not None:
			conn = None
			cursor = None
			try:
				conn = mysql.connector.connect(**config_mysql)
				cursor = conn.cursor()
				cursor.execute("DELETE FROM automovil WHERE id=%s", (self.id,))
				conn.commit()
				self.id = None
			except mysql.connector.Error as err:
				print(f"Error al eliminar automovil: {err}")
			finally:
				if cursor:
					try:
						cursor.close()
					except Exception as e:
						print(f"Error al cerrar el cursor: {e}")
				if conn:
					try:
						conn.close()
					except Exception as e:
						print(f"Error al cerrar la conexión: {e}")
