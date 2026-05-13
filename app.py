import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, render_template, Response, request, redirect, url_for
from modules.pose import generar_frames

# Importar capas de nuestra arquitectura hexagonal
from modules.infrastructure.mysql_adapter import db, MySQLUsuarioRepository
from modules.application.auth_service import AuthService

app = Flask(__name__)

# Configuración de la base de datos MySQL (Docker)
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = '3306' if db_host == 'db' else '3307'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://admin:pinguin123@{db_host}:{db_port}/pinguindance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos
db.init_app(app)

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Construcción de dependencias (Dependency Injection)
usuario_repository = MySQLUsuarioRepository()
auth_service = AuthService(usuario_repository)

@app.route('/')
def index():
    return render_template('index(actualizar_paraotravissta.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validar credenciales usando la capa de Servicio o Aplicación
        user = auth_service.autenticar_usuario(email, password)
        
        if user:
            return redirect(url_for('index'))
        else:
            error = 'Correo o contraseña incorrectos 👀'
            
    return render_template('Login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = "Las contraseñas no coinciden 🧊"
        else:
            try:
                # Usar el servicio para crear el usuario, él maneja las reglas de negocio
                auth_service.registrar_usuario(username, email, password)
                success = "¡Cuenta creada con éxito! Ya puedes iniciar sesión."
            except Exception as e:
                error = "El correo ya está registrado 🐧"
                
    return render_template('Regristrar.html', error=error, success=success)

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        pass
    return render_template('Cambiar_Contra.html')

@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
