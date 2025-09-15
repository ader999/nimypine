# cuentas/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si un usuario tiene uno de los roles permitidos.
    El 'es_admin_mipyme' siempre tiene acceso a todo.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Si el usuario no está logueado, redirigir a login
            if not request.user.is_authenticated:
                return redirect('cuentas:login')  # Asegúrate que esta sea tu URL de login

            # El admin general de la Mipyme (dueño) siempre tiene acceso
            if request.user.es_admin_mipyme:
                return view_func(request, *args, **kwargs)

            # Si el rol del usuario está en la lista de roles permitidos para esta vista
            if request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)

            # Si no cumple ninguna condición, se le niega el acceso.
            raise PermissionDenied

        return wrapper

    return decorator