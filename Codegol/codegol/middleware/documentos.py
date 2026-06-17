from django.shortcuts import redirect

from usuario.models import Usuario, Documentos
from usuario.forms import DOCUMENTOS_POR_ROL, es_menor


class BloqueoDocumentosMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        usuario_id = request.session.get("usuario_id")
        roles_sesion = request.session.get("roles", [])

        resolver = getattr(request, "resolver_match", None)
        url_name = getattr(resolver, "url_name", None)

        # 🔥 SI NO HAY URL (requests internos), dejar pasar
        if not url_name:
            return self.get_response(request)

        # 🔓 PÁGINAS LIBRES (NO SE BLOQUEAN NUNCA)
        RUTAS_LIBRES = [
            "login",
            "documentos",
            "admin:index",
        ]

        if url_name in RUTAS_LIBRES:
            return self.get_response(request)

        # 🔥 ADMIN NO TIENE BLOQUEOS
        if "Administrador" in roles_sesion:
            return self.get_response(request)

        # 🔐 SIN LOGIN
        if not usuario_id:
            return redirect("login")

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

            # 🔥 BLOQUEO GLOBAL SOLO SI HAY FALTANTES
            if len(faltantes) > 0:
                return redirect("documentos", id=usuario_id)

        except Usuario.DoesNotExist:
            return redirect("login")

        return self.get_response(request)
        