from .models import Usuario
import re

def generar_username_unico(nombre, apellido):
    """
    Genera un nombre de usuario único a partir del nombre y apellido.
    Ej: "Juan Pérez" -> "jperez", "jperez1", "jperez2", etc.
    """
    # 1. Limpiar y normalizar los strings
    # Tomamos la primera palabra del nombre y del apellido
    primer_nombre = nombre.split()[0].lower()
    primer_apellido = apellido.split()[0].lower()

    # Quitar caracteres no alfanuméricos
    primer_nombre = re.sub(r'[^a-z0-9]', '', primer_nombre)
    primer_apellido = re.sub(r'[^a-z0-9]', '', primer_apellido)

    # 2. Crear el nombre de usuario base
    base_username = f"{primer_nombre[0]}{primer_apellido}"
    username = base_username

    # 3. Asegurar la unicidad
    contador = 1
    while Usuario.objects.filter(username=username).exists():
        username = f"{base_username}{contador}"
        contador += 1

    return username