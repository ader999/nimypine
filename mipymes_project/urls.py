# mipymes_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('produccion/', include('produccion.urls')),

    path('marketplace/', include('marketplace.urls')),

    path('asistente/', include('asistente.urls')),

    # API URLs
    path('api/', include([
        path('cuentas/', include('cuentas.api_urls')),
        path('produccion/', include('produccion.api_urls')),
        path('asistente/', include('asistente.api_urls')),
    ])),

    # Cualquier URL que no sea /admin/ la enviará al urls.py de la app 'cuentas'
    path('', include('cuentas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'cuentas.views.manejador_error_403'
handler404 = 'cuentas.views.manejador_error_404'
handler500 = 'cuentas.views.manejador_error_500'

admin.site.site_header = "Administración de NIMYPINE" # El título principal en la cabecera
admin.site.site_title = "Portal de NIMYPINE"         # El título en la pestaña del navegador
admin.site.index_title = "Bienvenido al portal de administración" # El título en la página de inicio del admin
