from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from collections import defaultdict
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
from asistencia.models import Asistencia
from collections import defaultdict, OrderedDict
from decimal import Decimal
from .models import Rendimiento

from sesion_entrenamiento.models import (
    SesionEntrenamiento
)

from sesion_actividad.models import (
    SesionActividad
)

from asistencia.models import (
    Asistencia
)

from posicion_actividad.models import (
    PosicionActividad
)

from atributo_actividad.models import (
    ActividadAtributo
)
from django.db.models import Avg, Max

def tabla_rendimiento(
    request,
    id_sesion,
    id_categoria
):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id_sesion
    )

    # ==========================================
    # ACTIVIDADES CONGELADAS DE LA SESIÓN
    # ==========================================

    actividades_sesion = set(
        SesionActividad.objects.filter(
            sesion=sesion
        ).values_list(
            "actividad_id",
            flat=True
        )
    )

    # ==========================================
    # ASISTENCIAS DE LA CATEGORÍA
    # ==========================================

    asistencias = (
        Asistencia.objects
        .filter(
            id_sesion=sesion,
            id_categoria_id=id_categoria
        )
        .select_related(
            "id_matricula__id_jugador",
            "id_matricula__posicion"
        )
    )

    posiciones = OrderedDict()

    # ==========================================
    # RECORRER JUGADORES
    # ==========================================

    for asistencia in asistencias:

        matricula = asistencia.id_matricula

        jugador = matricula.id_jugador

        posicion = matricula.posicion

        nombre_posicion = posicion.nombre

        if nombre_posicion not in posiciones:

            posiciones[nombre_posicion] = {
                "columnas": [],
                "jugadores": OrderedDict()
            }

        # ==========================================
        # ACTIVIDADES VÁLIDAS PARA LA POSICIÓN
        # ==========================================

        actividades_posicion = set(
            PosicionActividad.objects.filter(
                posicion=posicion
            ).values_list(
                "actividad_id",
                flat=True
            )
        )

        actividades_validas = (
            actividades_sesion &
            actividades_posicion
        )

        if (
            matricula.id
            not in posiciones[nombre_posicion]["jugadores"]
        ):

            posiciones[nombre_posicion]["jugadores"][
                matricula.id
            ] = {
                "id": matricula.id,
                "nombre": jugador.nombre_completo,
                "celdas": {}
            }

        # ==========================================
        # ATRIBUTOS DE LAS ACTIVIDADES
        # ==========================================

        atributos_actividades = (
            ActividadAtributo.objects
            .filter(
                actividad_id__in=actividades_validas
            )
            .select_related(
                "actividad",
                "atributo"
            )
        )

        for aa in atributos_actividades:

            rendimiento, _ = (
                Rendimiento.objects.get_or_create(
                    matricula=matricula,
                    sesion=sesion,
                    actividad=aa.actividad,
                    atributo=aa.atributo,
                    id_categoria_id=id_categoria
                )
            )

            clave = (
                f"{aa.actividad.nombre} - "
                f"{aa.atributo.nombre}"
            )

            if (
                clave
                not in posiciones[
                    nombre_posicion
                ]["columnas"]
            ):

                posiciones[
                    nombre_posicion
                ]["columnas"].append(
                    clave
                )

            posiciones[
                nombre_posicion
            ]["jugadores"][
                matricula.id
            ]["celdas"][
                clave
            ] = {
                "id_rendimiento":
                rendimiento.id_rendimiento,

                "valor":
                rendimiento.valor
            }

    return render(
        request,
        "rendimiento/lista.html",
        {
            "posiciones": posiciones,
            "id_sesion": id_sesion,
            "id_categoria": id_categoria
        }
    )




def guardar_rendimiento(
    request,
    id_sesion,
    id_categoria
):

    if request.method == "POST":

        rendimientos = Rendimiento.objects.filter(
            sesion_id=id_sesion,
            id_categoria_id=id_categoria
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

    sesion = get_object_or_404(
    SesionEntrenamiento,
    id_sesion=id_sesion
)

    return redirect(
        'lista_sesiones',
        id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
    )


def historial_rendimiento(request):

    rendimientos = (
        Rendimiento.objects
        .filter(valor__isnull=False)
        .select_related(
            'matricula__id_jugador',
            'matricula__posicion',
            'actividad',
            'atributo',
            'sesion',
            'id_categoria'
        )
        .order_by(
            'matricula__id_jugador',
            'sesion__fecha'
        )
    )

    jugadores_dashboard = {}

    for r in rendimientos:

        jugador_id = r.matricula.id_jugador.id_usuario

        if jugador_id not in jugadores_dashboard:

            foto = None

            if r.matricula.id_jugador.foto_perfil:
                foto = r.matricula.id_jugador.foto_perfil.url

            jugadores_dashboard[jugador_id] = {
                "id": jugador_id,
                "nombre": r.matricula.id_jugador.nombre_completo,
                "foto": foto,
                "categoria": r.id_categoria.nombre_categoria,
                "posicion": (
                    r.matricula.posicion.nombre
                    if r.matricula.posicion
                    else "Sin posición"
                ),
                "valores": [],
                "atributos": defaultdict(list),
                "fechas": [],
                "promedios_fecha": {}
            }

        valor_float = float(r.valor)

        jugadores_dashboard[jugador_id]["valores"].append(
            valor_float
        )

        jugadores_dashboard[jugador_id]["atributos"][
            r.atributo.nombre
        ].append(
            valor_float
        )

        fecha = r.sesion.fecha.strftime(
            "%d/%m/%Y"
        )

        if (
            fecha
            not in jugadores_dashboard[
                jugador_id
            ]["promedios_fecha"]
        ):

            jugadores_dashboard[
                jugador_id
            ]["promedios_fecha"][
                fecha
            ] = []

        jugadores_dashboard[
            jugador_id
        ]["promedios_fecha"][
            fecha
        ].append(
            valor_float
        )

    # ===================================
    # ARMAR TARJETAS
    # ===================================

    tarjetas_jugadores = []

    for jugador in jugadores_dashboard.values():

        promedio_general = round(
            sum(jugador["valores"]) /
            len(jugador["valores"]),
            2
        )

        # --------------------
        # Mejor atributo
        # --------------------

        mejor_atributo = ""

        mejor_valor = 0

        peor_atributo = ""

        peor_valor = 999

        for atributo, valores in (
            jugador["atributos"].items()
        ):

            promedio = (
                sum(valores)
                / len(valores)
            )

            if promedio > mejor_valor:

                mejor_valor = promedio

                mejor_atributo = atributo

            if promedio < peor_valor:

                peor_valor = promedio

                peor_atributo = atributo

        # --------------------
        # Evolución temporal
        # --------------------

        fechas = []

        promedios = []

        for fecha, valores in (
            jugador["promedios_fecha"].items()
        ):

            fechas.append(fecha)

            promedios.append(
                round(
                    sum(valores)
                    / len(valores),
                    2
                )
            )

        tendencia = "→ Estable"

        if len(promedios) >= 2:

            if promedios[-1] > promedios[0]:

                tendencia = "↑ Mejorando"

            elif promedios[-1] < promedios[0]:

                tendencia = "↓ Bajando"

        tarjetas_jugadores.append({

            "id": jugador["id"],

            "nombre": jugador["nombre"],

            "foto": jugador["foto"],

            "categoria": jugador["categoria"],

            "posicion": jugador["posicion"],

            "promedio": promedio_general,

            "tendencia": tendencia,

            "mejor_atributo": mejor_atributo,

            "mejor_valor": round(
                mejor_valor,
                2
            ),

            "peor_atributo": peor_atributo,

            "peor_valor": round(
                peor_valor,
                2
            ),

            "fechas": fechas,

            "promedios": promedios

        })

    # ===================================
    # ORDENAR MEJORES JUGADORES
    # ===================================

    tarjetas_jugadores.sort(
        key=lambda x: x["promedio"],
        reverse=True
    )

    top_jugadores = tarjetas_jugadores[:3]

    jugadores = sorted([
        t["nombre"]
        for t in tarjetas_jugadores
    ])

    categorias = sorted(
        list(
            set(
                t["categoria"]
                for t in tarjetas_jugadores
            )
        )
    )
    # ==============================
    # KPIs del dashboard
    # ==============================

    total_jugadores = len(tarjetas_jugadores)

    if tarjetas_jugadores:
        promedio_club = round(
            sum(j["promedio"] for j in tarjetas_jugadores)
            / total_jugadores,
            2
        )
    else:
        promedio_club = 0

    jugadores_mejorando = sum(
        1 for j in tarjetas_jugadores
        if "Mejorando" in j["tendencia"]
    )

    jugadores_bajando = sum(
        1 for j in tarjetas_jugadores
        if "Bajando" in j["tendencia"]
    )
    return render(
    request,
    "rendimiento/historial.html",
    {
        "tarjetas_jugadores": tarjetas_jugadores,
        "top_jugadores": top_jugadores,
        "ranking": tarjetas_jugadores,
        "jugadores": jugadores,
        "categorias": categorias,

        "total_jugadores": total_jugadores,
        "promedio_club": promedio_club,
        "jugadores_mejorando": jugadores_mejorando,
        "jugadores_bajando": jugadores_bajando,
    }
)