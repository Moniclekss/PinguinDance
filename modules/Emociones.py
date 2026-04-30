import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)
print("Iniciando detector de emociones...")
print("NOTA: la primera vez peude tardar.")


cv2.namedWindow('Detector de Emociones', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Detector de Emociones', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


Ultima_emocion = "Buscando rostro..."
contaador_frames = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("No se pudo acceder a la cámara.")
        break

    frame = cv2.flip(frame, 1)  # Voltear como espejo

    if contaador_frames % 10 == 0:  # Analizar cada 10 frames para mejorar rendimiento
        try:
            resultado = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            if resultado and 'dominant_emotion' in resultado[0]:
                Ultima_emocion = resultado[0]['dominant_emotion']
        except:
            Ultima_emocion = "Error al detectar emociones."

    contaador_frames += 1

    cv2.putText(frame, f"Emocion: {Ultima_emocion}", (10, 30), 
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow('Detector de Emociones', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()        