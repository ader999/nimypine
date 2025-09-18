from django.urls import path
from . import views

app_name = 'asistente'

urlpatterns = [
    path('', views.asistente_view, name='asistente'),
]