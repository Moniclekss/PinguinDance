from flask_sqlalchemy import SQLAlchemy
from modules.domain.usuario import Usuario, IUsuarioRepository

db = SQLAlchemy()

# Modelo de SQLAlchemy (Base de datos real)
class UsuarioModel(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Adaptador: Implementa el Puerto usando SQLAlchemy (MySQL)
class MySQLUsuarioRepository(IUsuarioRepository):
    def guardar(self, usuario: Usuario):
        nuevo_user_db = UsuarioModel(
            username=usuario.username,
            email=usuario.email,
            password=usuario.password
        )
        db.session.add(nuevo_user_db)
        db.session.commit()

    def buscar_por_email(self, email: str) -> Usuario:
        user_db = UsuarioModel.query.filter_by(email=email).first()
        if user_db:
            return Usuario(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                password=user_db.password
            )
        return None