from werkzeug.security import generate_password_hash, check_password_hash
from modules.domain.usuario import Usuario, IUsuarioRepository

class AuthService:
    def __init__(self, repository: IUsuarioRepository):
        # Inyección de dependencias
        self.repository = repository

    def registrar_usuario(self, username, email, password):
        # Validar si existe
        if self.repository.buscar_por_email(email):
            raise Exception("El email ya está registrado.")
            
        hashed_pw = generate_password_hash(password, method='wsgi_context')
        nuevo_usuario = Usuario(username=username, email=email, password=hashed_pw)
        self.repository.guardar(nuevo_usuario)

    def autenticar_usuario(self, email, password):
        usuario = self.repository.buscar_por_email(email)
        if usuario and check_password_hash(usuario.password, password):
            return usuario
        return None