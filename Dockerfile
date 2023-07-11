# Imagen base
FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Establecer la variable de entorno para el archivo principal del proyecto
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Comando para ejecutar tu proyecto
CMD ["python", "songs.py"]
