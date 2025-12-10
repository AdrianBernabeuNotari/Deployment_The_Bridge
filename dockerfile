# Usa una imagen base de Python ligera (Alpine es pequeño y rápido)
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias y las instala PRIMERO (por rendimiento de caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
# Esto incluye app.py, create_db.py y la carpeta templates/
COPY . .

# Haz el script de entrada ejecutable
RUN chmod +x entrypoint.sh

# Expone el puerto que usa Flask por defecto
EXPOSE 5000

# Usa el script como punto de entrada
ENTRYPOINT ["./entrypoint.sh"]