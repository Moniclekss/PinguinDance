# PinguinDance
Pinguino bailando 
Para lograr que el pinguino y la camara se active se necesita lo siguinete 

# 1. Para la cámara, imágenes y el rastreo del cuerpo:
pip install opencv-python
pip install mediapipe
pip install pillow

# 2. Para la detección de rostros y emociones:
pip install deepface
pip install tf-keras

# 3. Para la interfaz gráfica moderna:
pip install customtkinter

# 4. Para la nueva interfaz web (Servidor):
pip install flask

# 5. Para la base de datos y seguridad:
pip install Flask-SQLAlchemy
pip install pymysql
pip install cryptography

# Pasos para ejecutar el proyecto web:
1. Encender la base de datos (Docker):
docker compose up -d

2. Iniciar el servidor web:
python app.py 

Si quiere solo usar los .py 
python modules\Emociones.py
Para que asi Funcione