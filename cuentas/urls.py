# cuentas/urls.py

from django.urls import path, include
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
    path('no-mipyme-asociada/', views.no_mipyme_asociada, name='no_mipyme_asociada'),

    # --- PASSWORD RESET URLS ---
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    
    # path('password_reset/done/') -> YA NO SE USA (se maneja con AJAX)
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='cuentas/password_reset_confirm.html',
        success_url='/cuentas/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='cuentas/password_reset_complete.html'
    ), name='password_reset_complete'),
]