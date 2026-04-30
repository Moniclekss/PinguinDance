import customtkinter as ctk
import cv2
from PIL import Image

# Configurar el tema visual moderno de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PinguinDanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURACIÓN DE LA PANTALLA PRINCIPAL ---
        self.title("Pinguin Dance - Just Dance Edition")
        self.geometry("900x600")
        
        # Grid para dividir la pantalla en dos (Menú Izquierdo / Video Abajo)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL LATERAL (BOTONES) ---
        self.frame_izquierdo = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_izquierdo.grid(row=0, column=0, sticky="nsew")
        self.frame_izquierdo.grid_rowconfigure(4, weight=1)

        self.label_titulo = ctk.CTkLabel(self.frame_izquierdo, text="PINGUIN DANCE", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botón 1: Iniciar Juego (Conecta con MediaPipe pronto)
        self.btn_jugar = ctk.CTkButton(self.frame_izquierdo, text="▶ Iniciar Baile", font=ctk.CTkFont(size=14))
        self.btn_jugar.grid(row=1, column=0, padx=20, pady=10)

        # Botón 2: Activar detector de Emociones
        self.btn_emociones = ctk.CTkButton(self.frame_izquierdo, text="1️⃣ Test Emociones (DeepFace)")
        self.btn_emociones.grid(row=2, column=0, padx=20, pady=10)
        
        # Botón 3: Detener cámara
        self.btn_detener = ctk.CTkButton(self.frame_izquierdo, text="🛑 Detener Cámara", fg_color="#b53333", hover_color="#8f2020")
        self.btn_detener.grid(row=3, column=0, padx=20, pady=40)

        self.label_estado = ctk.CTkLabel(self.frame_izquierdo, text="Estado: Esperando jugador...", text_color="gray")
        self.label_estado.grid(row=5, column=0, padx=20, pady=20, sticky="s")

        # --- ÁREA PRINCIPAL (DONDE IRÁ LA CÁMARA) ---
        self.frame_derecho = ctk.CTkFrame(self)
        self.frame_derecho.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_derecho.grid_rowconfigure(0, weight=1)
        self.frame_derecho.grid_columnconfigure(0, weight=1)

        # Aquí "dormirá" el video de OpenCV, por ahora ponemos un cuadro de espera
        self.label_video = ctk.CTkLabel(self.frame_derecho, text="📷 Presiona 'Iniciar Baile' para encender tu cámara web", 
                                        font=ctk.CTkFont(size=16), text_color="gray")
        self.label_video.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = PinguinDanceApp()
    app.mainloop()
