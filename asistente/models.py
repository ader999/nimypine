from django.db import models
from cuentas.models import Usuario

class Conversacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='conversaciones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Conversación de {self.usuario.username} - {self.fecha_inicio}"

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    contenido = models.TextField()
    es_usuario = models.BooleanField(default=True)  # True si es mensaje del usuario, False si es respuesta del asistente
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tipo = "Usuario" if self.es_usuario else "Asistente"
        return f"{tipo}: {self.contenido[:50]}..."

class GuiaUsuario(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    pasos = models.TextField()  # Pasos en formato texto o JSON
    palabras_clave = models.CharField(max_length=500, blank=True, null=True)  # Para buscar coincidencias
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
