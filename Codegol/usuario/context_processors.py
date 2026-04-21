from .models import Usuario, Documentos
from .forms import DOCUMENTOS_POR_ROL, es_menor

def documentos_faltantes(request):

    usuario_id = request.session.get("usuario_id")
    faltantes_nombres = []

    if usuario_id:
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)

            roles_usuario = usuario.roles.values_list('rol_usuario', flat=True)

            documentos_requeridos = set()

            for rol in roles_usuario:
                if rol == "Jugador" and es_menor(usuario):
                    documentos_requeridos.update(DOCUMENTOS_POR_ROL.get("JugadorMenor", []))
                else:
                    documentos_requeridos.update(DOCUMENTOS_POR_ROL.get(rol, []))

            documentos_subidos = set(
                Documentos.objects.filter(usuario=usuario)
                .values_list('tipo_documento', flat=True)
            )

            faltantes = documentos_requeridos - documentos_subidos

            diccionario_docs = dict(Documentos.DOCUMENTACION)
            faltantes_nombres = [diccionario_docs.get(f, f) for f in faltantes]

        except Usuario.DoesNotExist:
            pass

    return {
        "faltantes": faltantes_nombres
    }
