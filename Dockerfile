# Usar una imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que la aplicación Flask escucha
EXPOSE 8080

# Establecer la variable de entorno para Flask
ENV FLASK_APP=main.py

# Ejecutar la aplicación cuando el contenedor se inicie
CMD ["flask", "run", "--host=0.0.0.0"]