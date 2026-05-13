from abc import ABC, abstractmethod

# Entidad de Dominio (Pura de Python, sin saber sobre base de datos o web)
class Usuario:
    def __init__(self, username, email, password, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# Puerto: Define el contrato de lo que necesitamos de la base de datos
class IUsuarioRepository(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario):
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario:
        pass