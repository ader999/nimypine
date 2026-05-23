from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from .api_views import ChatbotAPIView

app_name = 'asistente_api'


class AllowAnyObtainAuthToken(ObtainAuthToken):
    """ObtainAuthToken with AllowAny permissions for unauthenticated access."""
    permission_classes = [AllowAny]


urlpatterns = [
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('api-token-auth/', AllowAnyObtainAuthToken.as_view(), name='api_token_auth'),
]
