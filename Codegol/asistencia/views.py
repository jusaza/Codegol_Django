from django.shortcuts import render, get_object_or_404, redirect
from .models import Asistencia
from sesion_entrenamiento.models import SesionEntrenamiento
from matricula.models import HistorialCategoria


def tabla_asistencia(request, id_sesion, id_categoria):

    sesion = get_object_or_404(SesionEntrenamiento, id_sesion=id_sesion)

    historiales = HistorialCategoria.objects.filter(
        id_categoria_id=id_categoria,
        estado=True
    ).select_related('id_matricula__id_jugador')

    matriculas = [h.id_matricula for h in historiales]

    asistencias = []

    for m in matriculas:
        a, _ = Asistencia.objects.get_or_create(
            id_sesion=sesion,
            id_matricula=m
        )
        asistencias.append(a)

    asistencias = sorted(
        asistencias,
        key=lambda x: x.id_matricula.id_jugador.nombre_completo.lower()
    )

    return render(request, 'asistencia/lista.html', {
        'asistencias': asistencias,
        'id_sesion': id_sesion,
    })


def guardar_asistencia(request, id_sesion):

    if request.method == "POST":

        asistencias = Asistencia.objects.filter(id_sesion=id_sesion)

        for a in asistencias:
            id_a = a.id_asistencia

            tipo = request.POST.get(f"tipo_{id_a}")
            just = request.POST.get(f"just_{id_a}")
            obs = request.POST.get(f"obs_{id_a}")

            if tipo:  # 🔥 evita guardar vacío
                a.tipo_asistencia = tipo
                a.justificacion = just
                a.observaciones = obs
                a.save()

    return redirect(request.META.get('HTTP_REFERER'))