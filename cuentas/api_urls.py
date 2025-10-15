# cuentas/api_urls.py

from django.urls import path
from .api_views import RegisterAPIView, LoginAPIView, LogoutAPIView

app_name = 'cuentas_api'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
]