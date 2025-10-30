# marketplace/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La URL /marketplace/ se mapeará a la vista listado_plantillas
    path('', views.listado_plantillas, name='marketplace_listado'),

    # La URL /marketplace/5/ (por ejemplo) se mapeará a la vista de detalle
    path('<int:plantilla_id>/', views.detalle_plantilla, name='marketplace_detalle'),
    path('subir/', views.subir_plantilla_view, name='marketplace_subir'),
    path('<int:plantilla_id>/descargar/', views.descargar_plantilla, name='marketplace_descargar'),
    path('pago_exitoso/<int:plantilla_id>/', views.pago_exitoso, name='marketplace_pago_exitoso'),
    path('pago_cancelado/<int:plantilla_id>/', views.pago_cancelado, name='marketplace_pago_cancelado'),
    path('perfil/', views.perfil_creador, name='marketplace_perfil'),

    path('productos/', views.lista_productos_marketplace, name='marketplace_lista_productos'),
]