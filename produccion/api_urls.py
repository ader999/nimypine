from django.urls import path
from .api_views import ProductListAPIView, CrearVentaAPIView

app_name = 'produccion_api'

urlpatterns = [
    path('productos/', ProductListAPIView.as_view(), name='lista_productos'),
    path('registrar-venta/', CrearVentaAPIView.as_view(), name='registrar_venta'),
]