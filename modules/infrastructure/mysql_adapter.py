from flask_sqlalchemy import SQLAlchemy
from modules.domain.modelos import Empleado, Asistencia, IEmpleadoRepository, IAsistenciaRepository
from datetime import datetime

db = SQLAlchemy()

class EmpleadoModel(db.Model):
    __tablename__ = 'empleado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cara_vector = db.Column(db.Text, nullable=True) # Vector json de la cara
    rol = db.Column(db.String(20), default='empleado')

class AsistenciaModel(db.Model):
    __tablename__ = 'asistencia'
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleado.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # ENTRADA / SALIDA
    fecha_hora = db.Column(db.DateTime, default=datetime.now)

class MySQLEmpleadoRepository(IEmpleadoRepository):
    def guardar(self, emp: Empleado):
        db_emp = EmpleadoModel(nombre=emp.nombre, email=emp.email, password=emp.password, cara_vector=emp.cara_vector, rol=emp.rol)
        db.session.add(db_emp)
        db.session.commit()
        
    def buscar_por_email(self, email: str) -> Empleado:
        db_emp = EmpleadoModel.query.filter_by(email=email).first()
        if db_emp:
            return Empleado(id=db_emp.id, nombre=db_emp.nombre, email=db_emp.email, password=db_emp.password, cara_vector=db_emp.cara_vector, rol=db_emp.rol)
        return None
        
    def obtener_todos(self):
        db_emps = EmpleadoModel.query.all()
        return [Empleado(id=e.id, nombre=e.nombre, email=e.email, password=e.password, cara_vector=e.cara_vector, rol=e.rol) for e in db_emps]
        
    def actualizar(self, emp: Empleado):
        db_emp = EmpleadoModel.query.filter_by(email=emp.email).first()
        if db_emp:
            db_emp.password = emp.password
            db_emp.cara_vector = emp.cara_vector
            db.session.commit()

class MySQLAsistenciaRepository(IAsistenciaRepository):
    def registrar(self, asis: Asistencia):
        db_asis = AsistenciaModel(empleado_id=asis.empleado_id, tipo=asis.tipo, fecha_hora=asis.fecha_hora)
        db.session.add(db_asis)
        db.session.commit()
        
    def obtener_por_empleado(self, empleado_id: int):
        return AsistenciaModel.query.filter_by(empleado_id=empleado_id).order_by(AsistenciaModel.fecha_hora.desc()).all()
