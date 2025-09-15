# mipymes_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('produccion/', include('produccion.urls')),

    path('marketplace/', include('marketplace.urls')),

    # Cualquier URL que no sea /admin/ la enviará al urls.py de la app 'cuentas'
    path('', include('cuentas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'cuentas.views.permission_denied_view'

admin.site.site_header = "Administración de NIMYPINE" # El título principal en la cabecera
admin.site.site_title = "Portal de NIMYPINE"         # El título en la pestaña del navegador
admin.site.index_title = "Bienvenido al portal de administración" # El título en la página de inicio del admin
