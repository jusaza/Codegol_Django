from django.shortcuts import render, get_object_or_404, redirect
from .models import Asistencia
from sesion_entrenamiento.models import SesionEntrenamiento


def tabla_asistencia(request, id_sesion, id_categoria):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id_sesion
    )

    roles = request.session.get("roles", [])
    usuario_id = request.session.get("usuario_id")

    es_responsable = (
        "Administrador" in roles or
        sesion.id_entrenador_id == usuario_id
    )

    asistencias = Asistencia.objects.filter(
        id_sesion=sesion,
        id_categoria_id=id_categoria
    ).select_related(
        "id_matricula__id_jugador"
    )

    # Solo el jugador ve únicamente su asistencia
    if not es_responsable and "Jugador" in roles:
        asistencias = asistencias.filter(
            id_matricula__id_jugador_id=usuario_id
        )

    asistencias = sorted(
        asistencias,
        key=lambda x: x.id_matricula.id_jugador.nombre_completo.lower()
    )

    return render(
        request,
        "asistencia/lista.html",
        {
            "asistencias": asistencias,
            "id_sesion": id_sesion,
            "id_categoria": id_categoria,
            "es_responsable": es_responsable,
        }
    )


def guardar_asistencia(
    request,
    id_sesion,
    id_categoria
):

    roles = request.session.get("roles", [])

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id_sesion
    )

    es_responsable = (
        "Administrador" in roles or
        sesion.id_entrenador_id == request.session.get("usuario_id")
    )

    if not es_responsable:
        return redirect(
            "lista_sesiones",
            id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
        )

    if request.method == "POST":

        asistencias = Asistencia.objects.filter(
            id_sesion=id_sesion,
            id_categoria_id=id_categoria
        )

        for a in asistencias:

            id_a = a.id_asistencia

            tipo = request.POST.get(f"tipo_{id_a}")
            just = request.POST.get(f"just_{id_a}")
            obs = request.POST.get(f"obs_{id_a}")

            if tipo:

                a.tipo_asistencia = tipo
                a.justificacion = just
                a.observaciones = obs
                a.save()

    return redirect(
        "lista_sesiones",
        id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
    )