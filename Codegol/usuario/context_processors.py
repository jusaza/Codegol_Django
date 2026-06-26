from .models import Usuario, Documentos, HistorialDocumentos
from .forms import DOCUMENTOS_POR_ROL, es_menor


def documentos_faltantes(request):

    usuario_id = request.session.get("usuario_id")
    roles_sesion = request.session.get("roles", [])

    faltantes_nombres = []
    documentos_rechazados = []
    docs_completos = False

    # ===== SIN LOGIN =====

    if not usuario_id:

        return {
            "faltantes": [],
            "docs_completos": False,
            "documentos_rechazados": [],
        }

    # ===== ADMIN SIEMPRE COMPLETO =====

    if "Administrador" in roles_sesion:

        return {
            "faltantes": [],
            "docs_completos": True,
            "documentos_rechazados": [],
        }

    try:

        usuario = Usuario.objects.get(
            id_usuario=usuario_id
        )

        roles_usuario = usuario.roles.values_list(
            'rol_usuario',
            flat=True
        )

        documentos_requeridos = set()

        # ===== DOCUMENTOS REQUERIDOS =====

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

        # ===== NOMBRES =====

        diccionario_docs = dict(
            Documentos.DOCUMENTACION
        )

        faltantes_nombres = [

            diccionario_docs.get(f, f)

            for f in faltantes

        ]

        # ===== DEVOLUCIONES PENDIENTES DE RESUBIR =====

        if faltantes:
            historial_rechazados = HistorialDocumentos.objects.filter(
                usuario=usuario,
                tipo_documento__in=faltantes,
            ).order_by('-fecha_eliminacion')

            documentos_rechazados = [
                {
                    'nombre': registro.nombre,
                    'tipo': diccionario_docs.get(
                        registro.tipo_documento,
                        registro.tipo_documento,
                    ),
                    'observacion': registro.observaciones_rechazo,
                }
                for registro in historial_rechazados
            ]

        # ===== COMPLETOS =====

        docs_completos = (
            len(faltantes) == 0
        )

    except Usuario.DoesNotExist:

        pass

    return {

        "faltantes": faltantes_nombres,

        "docs_completos": docs_completos,

        "documentos_rechazados": documentos_rechazados,

    }