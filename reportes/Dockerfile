# Dockerfile para el microservicio de reportes
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .
COPY pyproject.toml .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/
COPY run_flask.py .

# Exponer el puerto
EXPOSE 8080

# Variables de entorno por defecto
ENV PYTHONPATH=/app/src
ENV FLASK_APP=run_flask.py

# Comando por defecto
CMD ["python", "run_flask.py"]
