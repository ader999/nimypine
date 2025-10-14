# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Copia el script de entrada y hazlo ejecutable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expone el puerto 8000
EXPOSE 8000

# Usa el entrypoint para recopilar estáticos y ejecutar el comando
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "mipymes_project.wsgi:application", "--bind", "0.0.0.0:4000"]