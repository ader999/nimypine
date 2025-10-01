# cuentas/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = 'cuentas'


urlpatterns = [
    # URLs de la app
    path('', views.pagina_inicio, name='inicio'),
    # URLs de autenticación
    path('login/', views.login_view, name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- NUEVAS URLS PARA GESTIÓN DE EQUIPO ---
    path('equipo/', views.lista_usuarios_mipyme, name='lista_equipo'),
    path('equipo/nuevo/', views.crear_usuario_mipyme, name='crear_usuario_equipo'),
    path('equipo/rol/<int:usuario_id>/', views.gestionar_rol_usuario, name='gestionar_rol'),
    path('registro/', views.pagina_seleccion_registro, name='seleccion_registro'),
    path('registro/creador/', views.registro_creador_view, name='registro_creador'),
    path('registro/mipyme/', views.registro_mipyme_view, name='registro_mipyme'),
    path('confirmar-email/', views.confirmar_email_view, name='confirmar_email'),
    path('crear-mipyme/', views.crear_mipyme_para_creador_view, name='crear_mipyme_para_creador'),
    path('test-email/', views.test_email_view, name='test_email'),
    path('no-mipyme-asociada/', views.no_mipyme_asociada, name='no_mipyme_asociada'),

]