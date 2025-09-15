# cuentas/admin.py
from django.contrib import admin
from .models import Usuario, Mipyme, TipoEmpresa # 👈 Añade TipoEmpresa

# Registra tus modelos aquí
admin.site.register(Usuario)
admin.site.register(Mipyme)
admin.site.register(TipoEmpresa) # 👈 REGISTRA EL NUEVO MODELO