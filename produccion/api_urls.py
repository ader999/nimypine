# produccion/api_urls.py

from django.urls import path
from .api_views import ProductListAPIView

app_name = 'produccion_api'

urlpatterns = [
    path('productos/', ProductListAPIView.as_view(), name='api_productos'),
]