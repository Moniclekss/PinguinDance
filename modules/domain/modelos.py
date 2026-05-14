from abc import ABC, abstractmethod
from datetime import datetime

class Empleado:
    def __init__(self, nombre, email, password, cara_vector=None, rol='empleado', id=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.cara_vector = cara_vector
        self.rol = rol

class Asistencia:
    def __init__(self, empleado_id, tipo, fecha_hora=None, id=None):
        self.id = id
        self.empleado_id = empleado_id
        self.tipo = tipo # 'ENTRADA' o 'SALIDA'
        self.fecha_hora = fecha_hora or datetime.now()

class IEmpleadoRepository(ABC):
    @abstractmethod
    def guardar(self, empleado: Empleado): pass
    @abstractmethod
    def buscar_por_email(self, email: str) -> Empleado: pass
    @abstractmethod
    def actualizar(self, empleado: Empleado): pass

class IAsistenciaRepository(ABC):
    @abstractmethod
    def registrar(self, asistencia: Asistencia): pass
    @abstractmethod
    def obtener_por_empleado(self, empleado_id: int): pass
