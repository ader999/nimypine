import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .models import Conversacion, Mensaje
from .serializers import ConversacionSerializer
from .views import procesar_mensaje

# Obtener el logger
logger = logging.getLogger(__name__)

class ChatbotAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info(f"ChatbotAPIView: Petición POST recibida del usuario {request.user.username}")
        mensaje_usuario = request.data.get('mensaje')
        conversacion_id = request.data.get('conversacion_id')
        modelo_seleccionado = request.data.get('modelo', 'openai')

        if not mensaje_usuario:
            return Response(
                {'error': 'El campo "mensaje" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversacion = None
        if conversacion_id:
            try:
                conversacion = Conversacion.objects.get(id=conversacion_id, usuario=request.user)
            except Conversacion.DoesNotExist:
                return Response(
                    {'error': 'Conversación no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Crear una nueva conversación si no se proporciona un ID
            conversacion = Conversacion.objects.create(
                usuario=request.user,
                titulo=mensaje_usuario[:50]
            )

        # Guardar mensaje del usuario
        Mensaje.objects.create(
            conversacion=conversacion,
            contenido=mensaje_usuario,
            es_usuario=True
        )

        # Procesar el mensaje para obtener la respuesta del asistente
        respuesta_asistente = procesar_mensaje(mensaje_usuario, request.user, modelo_seleccionado)

        # Guardar respuesta del asistente
        Mensaje.objects.create(
            conversacion=conversacion,
            contenido=respuesta_asistente,
            es_usuario=False
        )

        # Devolver la conversación actualizada
        serializer = ConversacionSerializer(conversacion)
        return Response(serializer.data, status=status.HTTP_200_OK)
