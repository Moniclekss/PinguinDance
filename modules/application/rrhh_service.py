from werkzeug.security import generate_password_hash, check_password_hash
from modules.domain.modelos import Empleado, Asistencia, IEmpleadoRepository, IAsistenciaRepository

class RRHHService:
    def __init__(self, emp_repo: IEmpleadoRepository, asis_repo: IAsistenciaRepository):
        self.emp_repo = emp_repo
        self.asis_repo = asis_repo

    def registrar_empleado(self, nombre, email, password, cara_vector=None):
        if self.emp_repo.buscar_por_email(email):
            raise Exception("El empleado (email) ya está registrado.")
            
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        nuevo_emp = Empleado(nombre=nombre, email=email, password=hashed_pw, cara_vector=cara_vector)
        self.emp_repo.guardar(nuevo_emp)

    def autenticar_empleado(self, email, password):
        emp = self.emp_repo.buscar_por_email(email)
        if emp and check_password_hash(emp.password, password):
            return emp
        return None

    def marcar_asistencia(self, empleado_id, tipo):
        nueva_asistencia = Asistencia(empleado_id=empleado_id, tipo=tipo)
        self.asis_repo.registrar(nueva_asistencia)
        
    def obtener_todos(self):
        return getattr(self.emp_repo, 'obtener_todos', lambda: [])()
