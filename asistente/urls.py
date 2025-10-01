from django.urls import path
from . import views

app_name = 'asistente'

urlpatterns = [
    path('', views.asistente_view, name='asistente'),
    path('<int:conversacion_id>/', views.asistente_view, name='asistente_conversacion'),
]