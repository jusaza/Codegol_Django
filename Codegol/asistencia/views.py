from django.shortcuts import render, get_object_or_404, redirect
from .models import Asistencia
from sesion_entrenamiento.models import SesionEntrenamiento


def tabla_asistencia(request, id_sesion, id_categoria):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id_sesion
    )

    asistencias = Asistencia.objects.filter(
        id_sesion=sesion,
        id_categoria_id=id_categoria
    ).select_related(
        'id_matricula__id_jugador'
    )

    asistencias = sorted(
        asistencias,
        key=lambda x: x.id_matricula.id_jugador.nombre_completo.lower()
    )

    return render(
        request,
        'asistencia/lista.html',
        {
            'asistencias': asistencias,
            'id_sesion': id_sesion,
            'id_categoria': id_categoria
        }
    )


def guardar_asistencia(
    request,
    id_sesion,
    id_categoria
):

    if request.method == "POST":

        asistencias = Asistencia.objects.filter(
            id_sesion=id_sesion,
            id_categoria_id=id_categoria
        )

        for a in asistencias:

            id_a = a.id_asistencia

            tipo = request.POST.get(
                f"tipo_{id_a}"
            )

            just = request.POST.get(
                f"just_{id_a}"
            )

            obs = request.POST.get(
                f"obs_{id_a}"
            )

            if tipo:

                a.tipo_asistencia = tipo
                a.justificacion = just
                a.observaciones = obs

                a.save()

    return redirect(
        request.META.get(
            'HTTP_REFERER'
        )
    )