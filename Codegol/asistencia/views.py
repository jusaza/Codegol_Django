from django.shortcuts import render
from django.db.models.functions import Lower
from .models import Asistencia
from rendimiento.models import Rendimiento
from django.http import JsonResponse



def tabla_asistencia(request, id_sesion):

    asistencias = Asistencia.objects.filter(
        id_sesion=id_sesion
    ).select_related(
        'id_matricula__id_jugador'
    ).order_by(
        Lower('id_matricula__id_jugador__nombre_completo')
    )

    rendimientos = Rendimiento.objects.filter(
        id_asistencia__in=asistencias
    )

    rendimientos_dict = {
        r.id_asistencia_id: r
        for r in rendimientos
    }

    data = []
    hay_rendimiento = False  # 🔥 CLAVE

    for a in asistencias:
        r = rendimientos_dict.get(a.id_asistencia)

        # 🔥 detectar si existe al menos uno activo
        if r and r.estado:
            hay_rendimiento = True

        data.append({
            'asistencia': a,
            'rendimiento': r if r and r.estado else None
        })

    return render(request, 'asistencia/lista.html', {
        'data': data,
        'id_sesion': id_sesion,
        'hay_rendimiento': hay_rendimiento  # 🔥 IMPORTANTE
    })




def guardar_asistencia(request, id_sesion):

    asistencias = Asistencia.objects.filter(id_sesion=id_sesion)

    for a in asistencias:

        id_a = a.id_asistencia

        # 🔹 ASISTENCIA
        a.tipo_asistencia = request.POST.get(f"tipo_{id_a}")
        a.justificacion = request.POST.get(f"just_{id_a}")
        a.observaciones = request.POST.get(f"obs_{id_a}")
        a.save()

        # 🔥 DETECTAR SI HAY DATOS DE RENDIMIENTO
        def_val = request.POST.get(f"def_{id_a}")

        if def_val is not None:
            # 👉 SI EXISTEN CAMPOS → GUARDAR

            r, created = Rendimiento.objects.get_or_create(
                id_asistencia=a
            )

            r.estado = True

            r.defensa = max(1, int(request.POST.get(f"def_{id_a}") or 1))
            r.pase = max(1, int(request.POST.get(f"pase_{id_a}") or 1))
            r.regate = max(1, int(request.POST.get(f"reg_{id_a}") or 1))
            r.tecnica = max(1, int(request.POST.get(f"tec_{id_a}") or 1))
            r.velocidad = max(1, int(request.POST.get(f"vel_{id_a}") or 1))
            r.potencia_tiro = max(1, int(request.POST.get(f"tir_{id_a}") or 1))

            r.posicion = request.POST.get(f"pos_{id_a}") or 'ND'
            r.observaciones = request.POST.get(f"obsr_{id_a}")

            r.save()

        else:
            # 👉 SI NO HAY CAMPOS → DESACTIVAR
            Rendimiento.objects.filter(
                id_asistencia=a
            ).update(estado=False)

    return JsonResponse({'ok': True})