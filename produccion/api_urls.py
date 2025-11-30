from django.urls import path
from .api_views import ProductListAPIView, CrearVentaAPIView, StoreProductListAPIView, ToggleTiendaVisibleView

app_name = 'produccion_api'

urlpatterns = [
    path('productos/', ProductListAPIView.as_view(), name='lista_productos'),
    path('registrar-venta/', CrearVentaAPIView.as_view(), name='registrar_venta'),
    path('store/products/', StoreProductListAPIView.as_view(), name='store_products'),
    path('store/toggle-visibility/', ToggleTiendaVisibleView.as_view(), name='toggle_store_visibility'),
]