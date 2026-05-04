from django.shortcuts import redirect
from functools import wraps

from .models import Usuario, Documentos
from .forms import DOCUMENTOS_POR_ROL, es_menor


# =========================
# DECORADOR ROLES
# =========================
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


# =========================
# BLOQUEO DOCUMENTOS
# =========================
def bloqueo_documentos_completos(vista):

    @wraps(vista)
    def wrapper(request, *args, **kwargs):

        usuario_id = request.session.get("usuario_id")
        roles_sesion = request.session.get("roles", [])

        if not usuario_id:
            return redirect("login")

        # ADMIN NO BLOQUEA
        if "Administrador" in roles_sesion:
            return vista(request, *args, **kwargs)

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)

            roles_usuario = usuario.roles.values_list('rol_usuario', flat=True)

            documentos_requeridos = set()

            for rol in roles_usuario:
                if rol == "Jugador" and es_menor(usuario):
                    documentos_requeridos.update(
                        DOCUMENTOS_POR_ROL.get("JugadorMenor", [])
                    )
                else:
                    documentos_requeridos.update(
                        DOCUMENTOS_POR_ROL.get(rol, [])
                    )

            documentos_subidos = set(
                Documentos.objects.filter(usuario=usuario)
                .values_list('tipo_documento', flat=True)
            )

            faltantes = documentos_requeridos - documentos_subidos

            # 🔥 BLOQUEO GENERAL
            if faltantes:

                url_name = getattr(request.resolver_match, "url_name", "")

                # SOLO PERMITIR MI PERFIL Y DOCUMENTOS
                if url_name not in ["mi_perfil", "documentos"]:
                    return redirect("documentos", id=usuario_id)

        except Usuario.DoesNotExist:
            return redirect("login")

        return vista(request, *args, **kwargs)

    return wrapper
