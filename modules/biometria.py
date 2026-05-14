import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import os

OJO_IZQUIERDO = [362, 385, 387, 263, 373, 380]
OJO_DERECHO = [33, 160, 158, 133, 153, 144]

def calcular_distancia(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def calcular_ear(ojo, face_landmarks, width, height):
    puntos = [(int(face_landmarks[i].x * width), int(face_landmarks[i].y * height)) for i in ojo]
    v1 = calcular_distancia(puntos[1], puntos[5])
    v2 = calcular_distancia(puntos[2], puntos[4])
    h1 = calcular_distancia(puntos[0], puntos[3])
    if h1 == 0:
        return 0
    return (v1 + v2) / (2.0 * h1)

def extraer_vector_facial(imagen_base64):
    try:
        import base64
        if "," in imagen_base64:
            imagen_base64 = imagen_base64.split(",")[1]
            
        img_data = base64.b64decode(imagen_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        base_options = python.BaseOptions(model_asset_path='assets/face_landmarker.task')
        options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
        detector = vision.FaceLandmarker.create_from_options(options)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        resultados = detector.detect(mp_image)
        if not resultados.face_landmarks:
            return None
            
        landmarks = resultados.face_landmarks[0]
        puntos_clave = [33, 263, 1, 61, 291, 199] 
        vector = []
        
        cx, cy = landmarks[1].x, landmarks[1].y
        for idx in puntos_clave:
            dist = math.hypot(landmarks[idx].x - cx, landmarks[idx].y - cy)
            vector.append(str(round(dist, 5)))
            
        return ",".join(vector)
    except Exception as e:
        print(f"Error extrayendo vector: {e}")
        return None

def comparar_vectores(v1_str, v2_str, umbral=0.05):
    if not v1_str or not v2_str: return False
    v1 = [float(x) for x in v1_str.split(",")]
    v2 = [float(x) for x in v2_str.split(",")]
    if len(v1) != len(v2): return False
    distancia_total = sum(abs(a - b) for a, b in zip(v1, v2))
    return distancia_total < umbral

def generar_frames_biometricos():
    base_options = python.BaseOptions(model_asset_path='assets/face_landmarker.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    
    cap = cv2.VideoCapture(0)
    
    parpadeo_detectado = False
    ear_umbral = 0.22 
    conteo_frames_cerrados = 0
    frames_requeridos = 2
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultados = detector.detect(mp_image)
        
        panel_info = np.zeros((h, 300, 3), dtype=np.uint8)
        cv2.rectangle(panel_info, (0,0), (300, h), (15, 15, 15), -1)
        
        color_caja = (0, 165, 255)
        estado_texto = "Buscando Rostro..."
        
        if resultados.face_landmarks:
            face_landmarks = resultados.face_landmarks[0]
            
            for lm in face_landmarks:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
            ear_izquierdo = calcular_ear(OJO_IZQUIERDO, face_landmarks, w, h)
            ear_derecho = calcular_ear(OJO_DERECHO, face_landmarks, w, h)
            ear_promedio = (ear_izquierdo + ear_derecho) / 2.0
            
            if ear_promedio < ear_umbral:
                conteo_frames_cerrados += 1
            else:
                if conteo_frames_cerrados >= frames_requeridos:
                    parpadeo_detectado = True
                conteo_frames_cerrados = 0
                
            color_caja = (0, 255, 0) if parpadeo_detectado else (0, 165, 255)
            estado_texto = "SUJETO VIVO" if parpadeo_detectado else "VERIFICANDO LIVENESS"
            
            cv2.putText(panel_info, f"EAR Ojos: {ear_promedio:.2f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(panel_info, f"Liveness: {'OK' if parpadeo_detectado else 'PENDIENTE'}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_caja, 1)
        
        cv2.putText(frame, estado_texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_caja, 2)
        cv2.putText(panel_info, "SISTEMA BIOMETRICO RRHH", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.line(panel_info, (10, 40), (290, 40), (255, 255, 255), 1)
        
        frame_final = np.hstack((frame, panel_info))
        ret, buffer = cv2.imencode('.jpg', frame_final)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    cap.release()
