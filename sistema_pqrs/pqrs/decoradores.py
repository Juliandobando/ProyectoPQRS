from django.shortcuts import redirect
from django.http import HttpResponse

def login_requerido(rol_permitido):
    def decorador(view_func):
        def _wrapped_view(request, *args, **kwargs):
            rol = request.session.get('rol')
            if rol != rol_permitido:
                return HttpResponse("Permiso denegado", status=403)
            #return render(request, 'pqrs/403.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorador

# pqrs/decoradores.py

def solo_admin(view_func):
    def _wrapped_view(request, *args, **kwargs):
        rol = request.session.get('rol')
        if rol != 'admin':
            return HttpResponse("Permiso denegado", status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

