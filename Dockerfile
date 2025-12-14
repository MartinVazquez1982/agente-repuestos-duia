# ====================================================================
# ETAPA 1: BUILDER - Instalación de dependencias y compilación
# Usamos una imagen base que es adecuada para compilar paquetes (como wheel)
# ====================================================================
FROM python:3.11-slim-buster AS builder

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo el archivo de requisitos e instala las dependencias. 
# Esto aprovecha el cache de Docker si los requisitos no cambian.
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# ====================================================================
# ETAPA 2: FINAL - Imagen de ejecución de producción
# Usamos una imagen base más pequeña para el contenedor final
# ====================================================================
FROM python:3.11-slim-buster

# Establece variables de entorno para mejorar el rendimiento de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo
WORKDIR /app

# Copia las dependencias instaladas de la etapa 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copia el código de tu aplicación
COPY . /app

# Crea un usuario no-root por seguridad
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Comando por defecto para ejecutar la aplicación
CMD ["python", "main.py"]