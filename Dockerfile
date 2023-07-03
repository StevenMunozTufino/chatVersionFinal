# Usar una imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que la aplicación Flask escucha
EXPOSE 5000

# Establecer la variable de entorno para Flask
#ENV FLASK_APP=app.py

# Ejecutar la aplicación cuando el contenedor se inicie
ENTRYPOINT ["python", "app.py"]

