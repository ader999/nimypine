from rest_framework import serializers
from .models import Mensaje, Conversacion

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'contenido', 'es_usuario', 'fecha']

class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)

    class Meta:
        model = Conversacion
        fields = ['id', 'usuario', 'fecha_inicio', 'titulo', 'mensajes']