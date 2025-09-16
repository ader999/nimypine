# cuentas/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render


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


def mipyme_requerida(view_func):
    """
    Decorador que verifica si un usuario autenticado tiene una Mipyme asociada.
    Si no la tiene, le muestra una página de advertencia.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Primero, asegurarnos de que el usuario está logueado
        if not request.user.is_authenticated:
            return redirect('cuentas:login')  # O tu URL de login

        # La comprobación principal: ¿tiene el usuario una Mipyme?
        # Usamos hasattr para evitar un error si el campo no existiera.
        if hasattr(request.user, 'mipyme') and request.user.mipyme is not None:
            # Si tiene Mipyme, se ejecuta la vista original.
            return view_func(request, *args, **kwargs)
        else:
            # Si no tiene Mipyme, renderizamos una plantilla de advertencia.
            return render(request, 'cuentas/no_mipyme_asociada.html')

    return wrapper