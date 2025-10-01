# marketplace/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La URL /marketplace/ se mapeará a la vista listado_plantillas
    path('', views.listado_plantillas, name='marketplace_listado'),

    # La URL /marketplace/5/ (por ejemplo) se mapeará a la vista de detalle
    path('<int:plantilla_id>/', views.detalle_plantilla, name='marketplace_detalle'),
    path('subir/', views.subir_plantilla_view, name='marketplace_subir'),

]