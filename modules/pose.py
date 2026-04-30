import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

# Conexiones principales del cuerpo
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
]

def cargar_frames_gif(ruta_gif, tamano):
    frames = []
    try:
        gif = Image.open(ruta_gif)
        for frame in range(0, gif.n_frames):
            gif.seek(frame)
            img_rgba = gif.convert("RGBA").resize((tamano, tamano))
            img_cv = np.array(img_rgba)
            img_bgr = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2BGRA)
            frames.append(img_bgr)
    except Exception as e:
        print(f"No se pudo cargar el GIF: {e}")
    return frames

def dibujar_esqueleto(imagen, landmarks):
    h, w, _ = imagen.shape
    puntos_px = []
    
    for idx, landmark in enumerate(landmarks):
        x_px = int(landmark.x * w)
        y_px = int(landmark.y * h)
        puntos_px.append((x_px, y_px))
        cv2.circle(imagen, (x_px, y_px), 4, (245, 117, 66), -1)

    for inicio, fin in POSE_CONNECTIONS:
        if inicio < len(puntos_px) and fin < len(puntos_px):
            pt1 = puntos_px[inicio]
            pt2 = puntos_px[fin]
            cv2.line(imagen, pt1, pt2, (245, 66, 230), 2)

def superponer_imagen(fondo, imagen_superponer, x_centro, y_centro):
    try:
        h, w, _ = imagen_superponer.shape
        y1, y2 = max(0, y_centro - h//2), min(fondo.shape[0], y_centro + h//2)
        x1, x2 = max(0, x_centro - w//2), min(fondo.shape[1], x_centro + w//2)
        y1o, y2o = max(0, -(y_centro - h//2)), min(h, h - ((y_centro + h//2) - fondo.shape[0]))
        x1o, x2o = max(0, -(x_centro - w//2)), min(w, w - ((x_centro + w//2) - fondo.shape[1]))

        if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o: return

        alpha_s = imagen_superponer[y1o:y2o, x1o:x2o, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            fondo[y1:y2, x1:x2, c] = (alpha_s * imagen_superponer[y1o:y2o, x1o:x2o, c] +
                                      alpha_l * fondo[y1:y2, x1:x2, c])
    except Exception as e:
        pass

def generar_frames():
    # Rutas actualizadas a la nueva carpeta assets
    ruta_gif = os.path.join('assets', 'pinguim-penguin.gif')
    ruta_modelo = os.path.join('assets', 'pose_landmarker_lite.task')
    
    frames_pinguino = cargar_frames_gif(ruta_gif, tamano=250)
    frame_actual_gif = 0

    base_options = python.BaseOptions(model_asset_path=ruta_modelo)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False,  
        num_poses=1
    )

    detector = vision.PoseLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        deteccion = detector.detect(mp_image)

        # Crear el lienzo del pingüino
        pantalla_pinguino = np.zeros((frame.shape[0], 400, 3), dtype=np.uint8)
        if len(frames_pinguino) > 0:
            superponer_imagen(pantalla_pinguino, frames_pinguino[frame_actual_gif], 200, frame.shape[0]//2)
            frame_actual_gif = (frame_actual_gif + 1) % len(frames_pinguino)

        if deteccion.pose_landmarks:
            pose = deteccion.pose_landmarks[0] 
            dibujar_esqueleto(frame, pose)

        # Unir la cámara y el pingüino lado a lado
        imagen_combinada = np.hstack((frame, pantalla_pinguino))

        # Convertir a formato JPEG para enviarlo a la web
        ret, buffer = cv2.imencode('.jpg', imagen_combinada)
        frame_bytes = buffer.tobytes()

        # Usar formato "multipart" (estándar para streaming de video HTTP)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
