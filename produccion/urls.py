# produccion/urls.py

from django.urls import path
from . import views

# Este nombre es útil para referenciar este conjunto de URLs desde otras partes del proyecto.
app_name = 'produccion'

urlpatterns = [
    # Cuando alguien visite la URL raíz de esta app (ej: /produccion/),
    # se ejecutará la vista 'panel_produccion'.
    # El 'name' nos permite referirnos a esta URL fácilmente en las plantillas y vistas.
    path('', views.panel_produccion, name='panel'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/exportar-excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/calculadora/', views.calculadora_lotes, name='calculadora_lotes'),
# --- NUEVA URL PARA EDITAR UN PRODUCTO ---
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
# --- NUEVA URL PARA ELIMINAR UN PRODUCTO ---
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # --- NUEVA URL PARA ELIMINAR UN ITEM DE LA FORMULACIÓN ---
    path('productos/<int:producto_id>/formulacion/eliminar/<int:item_id>/',
         views.eliminar_formulacion_item,
         name='eliminar_formulacion_item'),
    # --- NUEVA URL PARA EDITAR UN ITEM DE LA FORMULACIÓN ---
    path('productos/<int:producto_id>/formulacion/editar/<int:item_id>/',
         views.editar_formulacion_item,
         name='editar_formulacion_item'),
    path('insumos/', views.lista_insumos, name='lista_insumos'),
    path('insumos/nuevo/', views.crear_insumo, name='crear_insumo'),
    # --- NUEVA URL PARA EDITAR UN INSUMO ---
    path('insumos/editar/<int:insumo_id>/', views.editar_insumo, name='editar_insumo'),
    # --- NUEVA URL PARA ELIMINAR UN INSUMO ---
    path('insumos/eliminar/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),

    # --- NUEVAS URLS PARA PASOS DE PRODUCCIÓN ---
    path('productos/<int:producto_id>/paso/editar/<int:paso_id>/', views.editar_paso_produccion, name='editar_paso_produccion'),
    path('productos/<int:producto_id>/paso/eliminar/<int:paso_id>/', views.eliminar_paso_produccion, name='eliminar_paso_produccion'),

    # --- NUEVAS URLS PARA PROCESOS ---
    path('procesos/', views.lista_procesos, name='lista_procesos'),
    path('procesos/nuevo/', views.crear_proceso, name='crear_proceso'),
    path('procesos/editar/<int:proceso_id>/', views.editar_proceso, name='editar_proceso'),
    path('procesos/eliminar/<int:proceso_id>/', views.eliminar_proceso, name='eliminar_proceso'),

    # --- VENTAS / FACTURACIÓN ---
    path('ventas/registrar/', views.registrar_venta, name='registrar_venta'),
    path('ventas/historial/', views.historial_ventas, name='historial_ventas'),
    # --- CONFIGURACIÓN ---
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('configuracion/actualizar-perfil/', views.actualizar_perfil, name='actualizar_perfil'),
    path('configuracion/configurar-avatar/', views.configurar_avatar, name='configurar_avatar'),
    # --- CONFIGURACIÓN DE EMPRESA ---
    path('configuracion/editar-empresa/', views.editar_informacion_empresa, name='editar_informacion_empresa'),
    path('configuracion/configurar-logo/', views.configurar_logo, name='configurar_logo'),
    path('configuracion/cambiar-sector/', views.cambiar_sector_economico, name='cambiar_sector_economico'),
    path('configuracion/parametros-produccion/', views.configurar_parametros_produccion, name='configurar_parametros_produccion'),
    # --- IMPUESTOS ---
    path('impuestos/', views.gestion_impuestos, name='gestion_impuestos'),
]