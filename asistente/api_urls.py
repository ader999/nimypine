from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .api_views import ChatbotAPIView

app_name = 'asistente_api'

# Aplica el decorador para permitir el acceso sin autenticación solo a esta vista
decorated_obtain_auth_token = permission_classes([AllowAny])(obtain_auth_token)

urlpatterns = [
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('api-token-auth/', decorated_obtain_auth_token, name='api_token_auth'),
]