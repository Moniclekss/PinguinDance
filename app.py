import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
from modules.biometria import generar_frames_biometricos

# Importar capas de nuestra arquitectura hexagonal (NUEVO DOMINIO EMPLEADOS)
from modules.infrastructure.mysql_adapter import db, MySQLEmpleadoRepository, MySQLAsistenciaRepository
from modules.application.rrhh_service import RRHHService
from modules.biometria import generar_frames_biometricos, extraer_vector_facial, comparar_vectores

app = Flask(__name__)
# Llave secreta para poder usar 'session' en Flask
app.secret_key = 'pinguin_dance_super_secret_key'

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
empleado_repository = MySQLEmpleadoRepository()
asistencia_repository = MySQLAsistenciaRepository()
rrhh_service = RRHHService(empleado_repository, asistencia_repository)

@app.route('/')
def index():
    # En Fase 4 ya no requerimos login para el kiosko. El Kiosko está abierto y usa la cara.
    return render_template('Kiosko.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validar credenciales usando la capa de Servicio o Aplicación
        empleado = rrhh_service.autenticar_empleado(email, password)
        
        if empleado:
            # Creamos la sesión para este empleado
            session['usuario_email'] = empleado.email
            session['usuario_username'] = empleado.nombre
            session['usuario_id'] = empleado.id
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos 👀', 'error')
            
    return render_template('Login.html')

@app.route('/logout')
def logout():
    session.clear() # Borramos la sesión
    return redirect(url_for('login'))

@app.route('/marcar_asistencia', methods=['POST'])
def marcar_asistencia():
    tipo = request.form['tipo']
    foto_base64 = request.form.get('foto_base64')
    
    if not foto_base64:
        flash("La cámara no envió su imagen para verificación biométrica 📸", "error")
        return redirect(url_for('index'))
        
    vector_actual = extraer_vector_facial(foto_base64)
    if not vector_actual:
        flash("No se detectó un rostro de forma clara. Intente nuevamente. ❌", "error")
        return redirect(url_for('index'))
        
    empleados = rrhh_service.obtener_todos()
    empleado_identificado = None
    
    # Comparamos
    for emp in empleados:
        if emp.cara_vector:
            if comparar_vectores(vector_actual, emp.cara_vector):
                empleado_identificado = emp
                break
                
    if empleado_identificado:
        try:
            rrhh_service.marcar_asistencia(empleado_identificado.id, tipo)
            flash(f"¡Identidad Confirmada! Asistencia ({tipo}) registrada para: {empleado_identificado.nombre} ✅", "success")
        except Exception as e:
            flash(f"Error al registrar asistencia: {e}", "error")
    else:
        flash("Rostro no reconocido en la base de datos empresarial. 🛡️", "error")
        
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        foto_base64 = request.form.get('foto_base64')
        
        if password != confirm_password:
            flash("Las contraseñas no coinciden 🧊", "error")
        elif not foto_base64:
            flash("Se requiere foto biométrica del rostro", "error")
        else:
            try:
                # Extraemos los 468 puntos faciales
                vector_facial = extraer_vector_facial(foto_base64)
                if not vector_facial:
                    flash("No se detectó un rostro claro en la foto. Intente de nuevo.", "error")
                    return redirect(url_for('register'))
                    
                # Usar el servicio RRHH para crear el empleado junto con la biometría
                rrhh_service.registrar_empleado(username, email, password, cara_vector=vector_facial)
                flash("¡Empleado registrado biométricamente con éxito!", "success")
                return redirect(url_for('login'))
            except Exception as e:
                flash(str(e), "error")
                
    return render_template('Regristrar.html')

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        # En el futuro conectar con rrhh_service.cambiar_contrasena
        pass
    return render_template('Cambiar_Contra.html')

@app.route('/video_feed')
def video_feed():
    # Usamos nuestro nuevo motor de Biometría (Face Mesh & Liveness)
    return Response(generar_frames_biometricos(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
