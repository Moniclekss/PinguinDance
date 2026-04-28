import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Conexiones principales del cuerpo (ej. del 11 (hombro) al 13 (codo))
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
]

def cargar_frames_gif(ruta_gif, tamano):
    # Función para cargar y extraer cada imagen (frame) del GIF usando Pillow
    frames = []
    try:
        gif = Image.open(ruta_gif)
        for frame in range(0, gif.n_frames):
            gif.seek(frame)
            # Convertir el frame a RGBA para mantener la transparencia
            img_rgba = gif.convert("RGBA").resize((tamano, tamano))
            # Convertir de formato Pillow a formato OpenCV (Numpy)
            img_cv = np.array(img_rgba)
            # OpenCV usa BGR en vez de RGB, por lo que intercambiamos los colores
            img_bgr = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2BGRA)
            frames.append(img_bgr)
    except Exception as e:
        print(f"No se pudo cargar el GIF: {e}")
    return frames

def dibujar_esqueleto(imagen, landmarks):
    h, w, _ = imagen.shape
    puntos_px = []
    
    # Calcular y dibujar cada punto del cuerpo (articulaciones)
    for idx, landmark in enumerate(landmarks):
        # Convertir porcentaje (0 a 1) en píxeles (0 a Ancho/Alto de cámara)
        x_px = int(landmark.x * w)
        y_px = int(landmark.y * h)
        puntos_px.append((x_px, y_px))
        
        # Dibujar un círculo en cada articulación (naranja)
        cv2.circle(imagen, (x_px, y_px), 4, (245, 117, 66), -1)

    # Dibujar los huesos conectando las articulaciones (línea morada/rosa)
    for inicio, fin in POSE_CONNECTIONS:
        if inicio < len(puntos_px) and fin < len(puntos_px):
            pt1 = puntos_px[inicio]
            pt2 = puntos_px[fin]
            cv2.line(imagen, pt1, pt2, (245, 66, 230), 2)

def superponer_imagen(fondo, imagen_superponer, x_centro, y_centro):
    # Función para colocar una imagen con fondo transparente (Alpha)
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

# Cargar los fotogramas del GIF de Club Penguin
# Usando el nuevo archivo GIF que acabas de agregar
frames_pinguino = cargar_frames_gif('pinguim-penguin.gif', tamano=250)
frame_actual = 0



# Nombre del archivo modelo que vamos a descargar
nombre_modelo = 'pose_landmarker_lite.task' 

print("Cargando el modelo... Presiona 'q' para salir de la ventana de video.")

# Configurar las opciones (Usamos Tasks API)
base_options = python.BaseOptions(model_asset_path=nombre_modelo)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,  
    num_poses=1
)

# Crear el detector e iniciar cámara
with vision.PoseLandmarker.create_from_options(options) as detector:
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo acceder a la cámara.")
            break
            
        # Voltear como espejo (más intuitivo)
        frame = cv2.flip(frame, 1)

        # Convertir a formato MediaPipe Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Detectar la pose
        deteccion = detector.detect(mp_image)

        # Crear un cuadrado negro nuevo que existe fuera de tu cámara (400x400 píxeles)
        pantalla_pinguino = np.zeros((400, 400, 3), dtype=np.uint8)

        # Dibujar el pingüino animado dentro de esa pantalla negra aparte
        if len(frames_pinguino) > 0:
            # Ponemos al pingüino directamente en el centro (200, 200)
            superponer_imagen(pantalla_pinguino, frames_pinguino[frame_actual], 200, 200)
            
            # Avanzamos al siguiente frame del GIF
            frame_actual = (frame_actual + 1) % len(frames_pinguino)

        # Mostrar la ventana nueva (Aparte de la cámara)
        cv2.imshow('Pinguino Coreografo', pantalla_pinguino)

        # La Inteligencia Artificial sigue leyendo tu cuerpo en tu cámara.
        # Si en el futuro quieres saber si lo hiciste bien (como un puntaje en Just Dance),
        # usaremos esto:
        if deteccion.pose_landmarks:
            pose = deteccion.pose_landmarks[0] 
            # Aquí la IA sabe dónde están tus hombros, manos, etc.
            
            # Volvemos a llamar a la función para dibujarte el esqueleto encima de tu video
            dibujar_esqueleto(frame, pose)

        cv2.imshow('Club Penguin Dance - Tracking (Python 3.13)', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
