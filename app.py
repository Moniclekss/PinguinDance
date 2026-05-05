from flask import Flask, render_template, Response, request
from modules.pose import generar_frames

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí irá la lógica para validar el usuario más adelante
        pass
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Aquí irá la lógica para guardar el usuario más adelante
        pass
    return render_template('register.html')

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        # Aquí irá la lógica para enviar el correo de recuperación
        pass
    return render_template('recover.html')

@app.route('/video_feed')
def video_feed():
    # Retorna el video continuo usando el generador de OpenCV
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)