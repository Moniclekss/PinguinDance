from flask import Flask, render_template, Response
from modules.pose import generar_frames

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Retorna el video continuo usando el generador de OpenCV
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)