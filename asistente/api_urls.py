from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import ChatbotAPIView

app_name = 'asistente_api'

urlpatterns = [
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]