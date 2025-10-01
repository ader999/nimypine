# cuentas/admin.py
from django.contrib import admin
from .models import Usuario, Mipyme, TipoEmpresa, SectorEconomico

# Registra tus modelos aquí
admin.site.register(Usuario)
admin.site.register(Mipyme)
admin.site.register(TipoEmpresa) # 👈 REGISTRA EL NUEVO MODELO
admin.site.register(SectorEconomico) # 👈 REGISTRA EL NUEVO MODELO