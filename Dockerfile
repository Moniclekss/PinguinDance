FROM python:3.13-slim

# Instalar dependencias del sistema requeridas por OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar el archivo de dependencias y ejecutarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de tu proyecto al contenedor
COPY . .

# Exponer el puerto donde corre Flask
EXPOSE 5000

# Comando para arrancar el servidor
CMD ["python", "app.py"]