from src.Model.automovil_model import Automovil

class AutomovilController:
    @staticmethod
    def obtener_automovil_por_id(id):
        try:
            automovil = Automovil.obtener_automovil_por_id(id)
            if automovil:
                return {
                    "id": automovil.id,
                    "placa": automovil.placa,
                    "saldo": automovil.saldo
                }
            return None
        except Exception as e:
            print(f"Error en el controlador al obtener un automóvil por id: {e}")
            return None
        
    @staticmethod
    def obtener_automovil_por_placa(placa):
        try:
            automovil = Automovil.obtener_por_placa(placa)
            if automovil:
                return {
                    "id": automovil.id,
                    "placa": automovil.placa,
                    "saldo": automovil.saldo
                }
            return None
        except Exception as e:
            print(f"Error en el controlador al obtener un automóvil por placa: {e}")
            return None
        
    @staticmethod
    def crear_automovil(placa, saldo=0.0):
        try:
            automovil = Automovil.crear_automovil(placa=placa, saldo=saldo)
            automovil.guardar()
            if automovil.id:
                return {
                    "id": automovil.id,
                    "placa": automovil.placa,
                    "saldo": automovil.saldo
                }
            return None
        except Exception as e:
            print(f"Error en el controlador al crear un automóvil: {e}")
            return None
        
    @staticmethod
    def actualizar_automovil(id, placa=None, saldo=None):
        try:
            automovil = Automovil.obtener_automovil_por_id(id)
            if automovil:
                if placa is not None:
                    automovil.placa = placa
                if saldo is not None:
                    automovil.saldo = saldo
                automovil.guardar()
                return {
                    "id": automovil.id,
                    "placa": automovil.placa,
                    "saldo": automovil.saldo
                }
            return None
        except Exception as e:
            print(f"Error en el controlador al actualizar un automóvil: {e}")
            return None

    @staticmethod
    def eliminar_automovil(id):
        try:
            automovil = Automovil.obtener_automovil_por_id(id)
            if automovil:
                automovil.eliminar()
                return True
            return False
        except Exception as e:
            print(f"Error en el controlador al eliminar automovil: {e}")
            return False