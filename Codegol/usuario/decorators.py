from django.shortcuts import redirect
from functools import wraps
from .models import Usuario, Documentos
from .forms import DOCUMENTOS_POR_ROL, es_menor

def rol_requerido(roles_permitidos):

    def permiso(vista):

        @wraps(vista)
        def mostrar(request, *args, **kwargs):

            if "usuario_id" not in request.session:
                return redirect("login")

            roles = request.session.get("roles", [])

            if not any(rol in roles for rol in roles_permitidos):
                return redirect("error400")

            return vista(request, *args, **kwargs)

        return mostrar

    return permiso


def bloqueo_documentos_completos(vista):

    @wraps(vista)
    def wrapper(request, *args, **kwargs):

        usuario_id = request.session.get("usuario_id")
        roles_sesion = request.session.get("roles", [])

        # ===== SIN SESION =====

        if not usuario_id:
            return redirect("login")

        # ===== ADMIN NUNCA BLOQUEADO =====

        if "Administrador" in roles_sesion:

            request.session["docs_completos"] = True

            return vista(request, *args, **kwargs)

        try:

            usuario = Usuario.objects.get(
                id_usuario=usuario_id
            )

            roles_usuario = usuario.roles.values_list(
                'rol_usuario',
                flat=True
            )

            documentos_requeridos = set()

            # ===== DOCUMENTOS POR ROL =====

            for rol in roles_usuario:

                if rol == "Jugador" and es_menor(usuario):

                    documentos_requeridos.update(
                        DOCUMENTOS_POR_ROL.get(
                            "JugadorMenor",
                            []
                        )
                    )

                else:

                    documentos_requeridos.update(
                        DOCUMENTOS_POR_ROL.get(
                            rol,
                            []
                        )
                    )

            # ===== DOCUMENTOS SUBIDOS =====

            documentos_subidos = set(

                Documentos.objects.filter(
                    usuario=usuario
                ).values_list(
                    'tipo_documento',
                    flat=True
                )

            )

            # ===== FALTANTES =====

            faltantes = (
                documentos_requeridos -
                documentos_subidos
            )

            # ===== ACTUALIZAR SESION =====

            request.session["docs_completos"] = (
                len(faltantes) == 0
            )

            # ===== BLOQUEAR SI FALTAN =====

            
        except Usuario.DoesNotExist:

            return redirect("login")

        return vista(request, *args, **kwargs)

    return wrapper
