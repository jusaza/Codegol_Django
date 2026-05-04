from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from usuario.decorators import bloqueo_documentos_completos

from .models import Rendimiento
from sesion_entrenamiento.models import SesionEntrenamiento
from matricula.models import HistorialCategoria
from entrenamiento_actividad.models import EntrenamientoActividad
from posicion_actividad.models import PosicionActividad
from atributo_actividad.models import ActividadAtributo
from categoria.models import Categoria
from django.db.models import Avg


<<<<<<< HEAD
# 🔥 TABLA DE RENDIMIENTO (igual que antes)
@bloqueo_documentos_completos
=======
# 🔥 TABLA DE RENDIMIENTO (igual que antes + posición)
>>>>>>> 30385b46cebc1e81746169fab67ddd85956c8947
def tabla_rendimiento(request, id_sesion, id_categoria):

    sesion = get_object_or_404(SesionEntrenamiento, id_sesion=id_sesion)

    actividades_entrenamiento = EntrenamientoActividad.objects.filter(
        entrenamiento=sesion.id_entrenamiento
    ).values_list('actividad_id', flat=True)

    historiales = HistorialCategoria.objects.filter(
        id_categoria_id=id_categoria,
        estado=True
    ).select_related('id_matricula__id_jugador', 'id_matricula__posicion')

    data = []

    for h in historiales:

        m = h.id_matricula
        jugador = m.id_jugador
        posicion = m.posicion  # 👈 ya lo tenías

        actividades_posicion = PosicionActividad.objects.filter(
            posicion=posicion
        ).values_list('actividad_id', flat=True)

        actividades_validas = set(actividades_entrenamiento).intersection(actividades_posicion)

        for actividad_id in actividades_validas:

            atributos = ActividadAtributo.objects.filter(
                actividad_id=actividad_id
            ).select_related('atributo', 'actividad')

            for aa in atributos:

                rendimiento, _ = Rendimiento.objects.get_or_create(
                    matricula=m,
                    sesion=sesion,
                    actividad=aa.actividad,
                    atributo=aa.atributo
                )

                data.append({
                    'jugador_id': m.id,
                    'jugador_nombre': jugador.nombre_completo,
                    'posicion': posicion.nombre,  # 🔥 NUEVO (ÚNICO CAMBIO)
                    'actividad': aa.actividad.nombre,
                    'atributo': aa.atributo.nombre,
                    'valor': rendimiento.valor,
                    'id_rendimiento': rendimiento.id_rendimiento
                })

    return render(request, 'rendimiento/lista.html', {
        'data': data,
        'id_sesion': id_sesion,
        'id_categoria': id_categoria
    })


# 🔥 GUARDAR (SIN CAMBIOS)
def guardar_rendimiento(request, id_sesion):

    if request.method == "POST":

        rendimientos = Rendimiento.objects.filter(sesion_id=id_sesion)

        for r in rendimientos:
            valor = request.POST.get(f"valor_{r.id_rendimiento}")

            if valor:
                r.valor = float(valor)
                r.save()

        return redirect('historial_rendimiento')

    return JsonResponse({'ok': False})


# 🔥 HISTORIAL (SIN CAMBIOS)
def historial_rendimiento(request):

    rendimientos = Rendimiento.objects.filter(
        valor__isnull=False
    ).select_related(
        'matricula__id_jugador',
        'actividad',
        'atributo',
        'sesion'
    ).order_by('-sesion__fecha')

    data = []

    for r in rendimientos:

        historial = HistorialCategoria.objects.filter(
            id_matricula=r.matricula
        ).select_related('id_categoria').last()

        categoria = historial.id_categoria.nombre_categoria if historial else "Sin categoría"

        data.append({
            'jugador': r.matricula.id_jugador.nombre_completo,
            'categoria': categoria,
            'actividad': r.actividad.nombre,
            'atributo': r.atributo.nombre,
            'valor': r.valor,
            'fecha': r.sesion.fecha
        })

    jugadores = Rendimiento.objects.filter(
        valor__isnull=False
    ).values_list(
        'matricula__id_jugador__nombre_completo',
        flat=True
    ).distinct()

    categorias = list(set([
        d['categoria'] for d in data
    ]))

    promedios = Rendimiento.objects.filter(
        valor__isnull=False
    ).values(
        'matricula__id_jugador__nombre_completo'
    ).annotate(
        promedio=Avg('valor')
    )

    return render(request, 'rendimiento/historial.html', {
        'data': data,
        'promedios': promedios,
        'jugadores': jugadores,
        'categorias': categorias
    })