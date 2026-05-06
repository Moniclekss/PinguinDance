import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, render_template, Response, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modules.pose import generar_frames

app = Flask (__name__)

# Configuración de la base de datos MySQL (Docker)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:pinguin123@localhost:3306/pinguindance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuario para la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Buscar usuario en la base de datos
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Si es correcto, lo enviamos a la cámara
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
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            error = "Las contraseñas no coinciden 🧊"
        else:
            # Comprobar si el correo ya existe
            existe = Usuario.query.filter_by(email=email).first()
            if existe:
                error = "El correo ya está registrado 🐧"
            else:
                # Encriptar contraseña por seguridad
                hashed_pw = generate_password_hash(password)
                nuevo_usuario = Usuario(username=username, email=email, password=hashed_pw)
                
                # Guardar en Base de Datos
                db.session.add(nuevo_usuario)
                db.session.commit()
                success = "¡Cuenta creada con éxito! Ya puedes iniciar sesión."
                
    return render_template('Regristrar.html', error=error, success=success)

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        # Aquí irá la lógica para enviar el correo de recuperación
        pass
    return render_template('Cambiar_Contra.html')

@app.route('/video_feed')
def video_feed():
    # Retorna el video continuo usando el generador de OpenCV
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)