from django.shortcuts import redirect

def rol_requerido(roles_permitidos):

    def permiso(vista):

        def _wrapped_view(request, *args, **kwargs):

            if "usuario_id" not in request.session:
                return redirect("login")

            roles = request.session.get("roles", []) 

            # validar si tiene algun rol
            if not any(rol in roles for rol in roles_permitidos):
                return redirect("error400")

            return vista(request, *args, **kwargs)

        return _wrapped_view

    return permiso
