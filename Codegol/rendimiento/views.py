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
from decimal import Decimal

from collections import defaultdict, OrderedDict

def tabla_rendimiento(request, id_sesion, id_categoria):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id_sesion
    )

    actividades_entrenamiento = set(
        EntrenamientoActividad.objects.filter(
            entrenamiento=sesion.id_entrenamiento
        ).values_list(
            'actividad_id',
            flat=True
        )
    )

    historiales = HistorialCategoria.objects.filter(
        id_categoria_id=id_categoria,
        estado=True
    ).select_related(
        'id_matricula__id_jugador',
        'id_matricula__posicion'
    )

    posiciones = OrderedDict()

    for historial in historiales:

        matricula = historial.id_matricula
        jugador = matricula.id_jugador
        posicion = matricula.posicion

        nombre_posicion = posicion.nombre

        if nombre_posicion not in posiciones:
            posiciones[nombre_posicion] = {
                'columnas': [],
                'jugadores': OrderedDict()
            }

        actividades_posicion = set(
            PosicionActividad.objects.filter(
                posicion=posicion
            ).values_list(
                'actividad_id',
                flat=True
            )
        )

        actividades_validas = (
            actividades_entrenamiento &
            actividades_posicion
        )

        if matricula.id not in posiciones[nombre_posicion]['jugadores']:

            posiciones[nombre_posicion]['jugadores'][matricula.id] = {
                'id': matricula.id,
                'nombre': jugador.nombre_completo,
                'celdas': {}
            }

        for actividad_id in actividades_validas:

            atributos = ActividadAtributo.objects.filter(
                actividad_id=actividad_id
            ).select_related(
                'actividad',
                'atributo'
            )

            for aa in atributos:

                rendimiento, _ = Rendimiento.objects.get_or_create(
                    matricula=matricula,
                    sesion=sesion,
                    actividad=aa.actividad,
                    atributo=aa.atributo
                )

                clave = f"{aa.actividad.nombre} - {aa.atributo.nombre}"

                if clave not in posiciones[nombre_posicion]['columnas']:
                    posiciones[nombre_posicion]['columnas'].append(clave)

                posiciones[nombre_posicion]['jugadores'][matricula.id]['celdas'][clave] = {
                    'id_rendimiento': rendimiento.id_rendimiento,
                    'valor': rendimiento.valor
                }

    return render(
        request,
        'rendimiento/lista.html',
        {
            'posiciones': posiciones,
            'id_sesion': id_sesion,
            'id_categoria': id_categoria
        }
    )


def guardar_rendimiento(request, id_sesion):

    if request.method == "POST":

        rendimientos = Rendimiento.objects.filter(
            sesion_id=id_sesion
        )

        for r in rendimientos:

            valor = request.POST.get(
                f"valor_{r.id_rendimiento}"
            )

            if valor:

                valor = valor.replace(",", ".")

                r.valor = Decimal(valor)

            else:

                r.valor = None

            r.save()

        return redirect(
            'historial_rendimiento'
        )


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