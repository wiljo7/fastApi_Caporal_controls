# 1. Imagen base oficial de Python (versión ligera)
FROM python:3.10-slim

# 2. Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos dependencias del sistema necesarias para conectar con MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos solo el archivo de requerimientos primero (para aprovechar el cache de Docker)
COPY requirements.txt .

# 6. Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiamos todo el contenido de tu carpeta actual al contenedor
COPY . .

# 8. Exponemos el puerto en el que corre FastAPI (por defecto 8000)
EXPOSE 8000

# 9. Comando para arrancar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]