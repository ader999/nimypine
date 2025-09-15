# cuentas/urls.py

from django.urls import path
# 👇 Importamos las vistas de autenticación de Django
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'


urlpatterns = [
    # URLs de la app
    path('', views.pagina_inicio, name='inicio'),
    path('registro/', views.registro_mipyme, name='registro'),

    # URLs de autenticación usando las vistas de Django
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- NUEVAS URLS PARA GESTIÓN DE EQUIPO ---
    path('equipo/', views.lista_usuarios_mipyme, name='lista_equipo'),
    path('equipo/nuevo/', views.crear_usuario_mipyme, name='crear_usuario_equipo'),
    path('equipo/rol/<int:usuario_id>/', views.gestionar_rol_usuario, name='gestionar_rol'),


]