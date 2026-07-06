from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import SesionEntrenamiento
from entrenamientos.models import Entrenamiento
from usuario.models import Usuario
from categoria.models import Categoria
from matricula.models import HistorialCategoria, Matricula
from asistencia.models import Asistencia
from rendimiento.models import Rendimiento
from sesion_categoria.models import SesionCategoria
from entrenamiento_actividad.models import EntrenamientoActividad
from sesion_actividad.models import SesionActividad
from django.db.models import Q
from django.contrib import messages
from datetime import date
from movimiento_inventario.models import MovimientoInventario
from django.contrib import messages

def lista_sesiones(request, id_entrenamiento):

    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento
    )

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    # Prioridad de roles
    es_admin = "Administrador" in roles
    es_entrenador = (
        "Entrenador" in roles and
        not es_admin
    )
    es_jugador = (
        "Jugador" in roles and
        not es_admin and
        not es_entrenador
    )

    sesiones = SesionEntrenamiento.objects.filter(
        id_entrenamiento=entrenamiento,
        estado=True
    )

    # Filtrado según prioridad
    categoria_jugador_id = None

    if es_admin:
        pass

    elif es_entrenador:
        sesiones = sesiones.filter(
            id_entrenador_id=usuario_id
        )

    elif es_jugador:
        categoria_jugador_id = _categoria_jugador_id(
            usuario_id
        )

        if categoria_jugador_id:
            sesiones = sesiones.filter(
                sesioncategoria__id_categoria_id=categoria_jugador_id,
                sesioncategoria__estado=True,
            ).distinct()
        else:
            sesiones = sesiones.none()

    sesiones = (
        sesiones
        .select_related("id_entrenador")
        .order_by("-fecha")
    )

    entrenadores = Usuario.objects.filter(
        usuario__id_rol__rol_usuario__iexact="Entrenador"
    ).distinct()

    for sesion in sesiones:

        # Responsable de la sesión
        sesion.es_responsable = (
            es_admin or
            (
                "Entrenador" in roles and
                sesion.id_entrenador_id == usuario_id
            )
        )

        categorias_sesion = (
            SesionCategoria.objects.filter(
                id_sesion=sesion,
                estado=True
            )
        )

        # El jugador solo ve su categoría
        if categoria_jugador_id:
            categorias_sesion = categorias_sesion.filter(
                id_categoria_id=categoria_jugador_id
            )

        categorias_sesion = categorias_sesion.select_related(
            "id_categoria"
        )

        sesion.categorias_registradas = categorias_sesion

        for categoria in sesion.categorias_registradas:

            asistencias = Asistencia.objects.filter(
                id_sesion=sesion,
                id_categoria=categoria.id_categoria
            )

            pendientes = asistencias.filter(
                Q(tipo_asistencia__isnull=True) |
                Q(tipo_asistencia="")
            ).exists()

            categoria.asistencia_completa = not pendientes

        sesion.tiene_registros = (
            Asistencia.objects.filter(
                id_sesion=sesion
            ).exclude(
                Q(tipo_asistencia__isnull=True) |
                Q(tipo_asistencia="")
            ).exists() or
            Rendimiento.objects.filter(
                sesion=sesion,
                valor__isnull=False
            ).exists()
        )

    return render(
        request,
        "sesion_entrenamiento/lista.html",
        {
            "entrenamiento": entrenamiento,
            "sesiones": sesiones,
            "entrenadores": entrenadores,
            "categorias": Categoria.objects.filter(
                estado=True
            ),
        }
    )

def crear_sesion(request, id_entrenamiento):

    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento
    )

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    entrenadores = Usuario.objects.filter(
        usuario__id_rol__rol_usuario__iexact="Entrenador"
    ).distinct()

    entrenador_seleccionado = None

    if "Entrenador" in roles:

        entrenador_seleccionado = get_object_or_404(
            Usuario,
            id_usuario=usuario_id
        )

    if request.method == "POST":

        fecha = request.POST.get("fecha")
        if fecha < str(date.today()):

            messages.error(
                request,
                "No se pueden crear sesiones con fechas anteriores a hoy."
            )

            return redirect(
                "lista_sesiones",
                id_entrenamiento=id_entrenamiento
            )
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        categorias = request.POST.getlist("categorias[]")


        if "Administrador" in roles:

            entrenador_id = request.POST.get(
                "id_entrenador"
            )

            entrenador = get_object_or_404(
                Usuario,
                id_usuario=entrenador_id
            )

        else:

            entrenador = entrenador_seleccionado


        sesion = SesionEntrenamiento.objects.create(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=True,
            id_entrenador=entrenador,
            id_entrenamiento=entrenamiento
        )


        actividades_entrenamiento = (
            EntrenamientoActividad.objects
            .filter(
                entrenamiento=entrenamiento
            )
            .order_by("orden")
        )

        for actividad in actividades_entrenamiento:

            SesionActividad.objects.create(
                sesion=sesion,
                actividad=actividad.actividad,
                orden=actividad.orden,
                duracion_min=actividad.duracion_min
            )

        # ================= CATEGORÍAS DE LA SESIÓN =================

        categorias_procesadas = set()

        for id_categoria in categorias:

            if not id_categoria:
                continue

            if id_categoria in categorias_procesadas:
                continue

            categorias_procesadas.add(id_categoria)

            categoria = get_object_or_404(
                Categoria,
                id_categoria=id_categoria
            )

            # Relación sesión-categoría

            SesionCategoria.objects.update_or_create(
                id_sesion=sesion,
                id_categoria=categoria,
                defaults={
                    "estado": True
                }
            )

            # =====================================
            # CREAR ASISTENCIAS DE ESA CATEGORÍA
            # =====================================

            historiales = HistorialCategoria.objects.filter(
                id_categoria=categoria,
                estado=True,
                id_matricula__estado=True,
                id_matricula__id_jugador__estado=True,
                id_matricula__fecha_inicio__lte=sesion.fecha,
                id_matricula__fecha_fin__gte=sesion.fecha
            ).select_related(
                "id_matricula"
            )

            for historial in historiales:

                Asistencia.objects.get_or_create(
                    id_sesion=sesion,
                    id_matricula=historial.id_matricula,
                    id_categoria=categoria
                )

        return redirect(
            'lista_sesiones',
            id_entrenamiento=id_entrenamiento
        )

    return render(
        request,
        "sesion_entrenamiento/lista.html",
        {
            "entrenamiento": entrenamiento,
            "entrenadores": entrenadores,
            "categorias": Categoria.objects.filter(
                estado=True
            ),
            "es_admin": "Administrador" in roles
        }
    )


# ================= EDITAR =================
def editar_sesion(request, id):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id,
        estado=True
    )

    entrenamiento = sesion.id_entrenamiento

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    entrenadores = Usuario.objects.filter(
        usuario__id_rol__rol_usuario__iexact="Entrenador"
    ).distinct()

    entrenador_seleccionado = None

    if "Entrenador" in roles:

        entrenador_seleccionado = get_object_or_404(
            Usuario,
            id_usuario=usuario_id
        )

    if request.method == "POST":

        sesion.fecha = request.POST.get("fecha")
        sesion.hora_inicio = request.POST.get("hora_inicio")
        sesion.hora_fin = request.POST.get("hora_fin")

        # ================= ENTRENADOR =================

        if "Administrador" in roles:

            entrenador_id = request.POST.get(
                "id_entrenador"
            )

            if entrenador_id:

                sesion.id_entrenador = get_object_or_404(
                    Usuario,
                    id_usuario=entrenador_id
                )

        else:

            sesion.id_entrenador = entrenador_seleccionado

        sesion.save()

        # ================= CATEGORIAS =================

        categorias_nuevas = request.POST.getlist(
            "categorias[]"
        )

        categorias_nuevas = [
            int(c)
            for c in categorias_nuevas
            if c
        ]

        relaciones = SesionCategoria.objects.filter(
            id_sesion=sesion
        )

        # ==========================================
        # DESACTIVAR CATEGORÍAS ELIMINADAS
        # ==========================================

        relaciones.exclude(
            id_categoria_id__in=categorias_nuevas
        ).update(
            estado=False
        )

        # ==========================================
        # ACTIVAR O CREAR CATEGORÍAS
        # ==========================================

        for categoria_id in categorias_nuevas:

            relacion, creada = (
                SesionCategoria.objects.get_or_create(
                    id_sesion=sesion,
                    id_categoria_id=categoria_id,
                    defaults={
                        "estado": True
                    }
                )
            )

            if not creada and not relacion.estado:

                relacion.estado = True
                relacion.save()

        return redirect(
            "lista_sesiones",
            id_entrenamiento=entrenamiento.id_entrenamiento
        )

    # ==========================================
    # CATEGORÍAS ACTIVAS DE LA SESIÓN
    # ==========================================

    categorias_sesion = (
        SesionCategoria.objects
        .filter(
            id_sesion=sesion,
            estado=True
        )
        .select_related("id_categoria")
    )

    return render(
        request,
        "sesion_entrenamiento/lista.html",
        {
            "sesion": sesion,
            "entrenamiento": entrenamiento,
            "entrenadores": entrenadores,
            "es_admin": "Administrador" in roles,

            # todas las categorías disponibles
            "categorias": Categoria.objects.filter(
                estado=True
            ),

            # categorías ya registradas en la sesión
            "categorias_sesion": categorias_sesion
        }
    )


# ================= ELIMINAR =================
def eliminar_sesion(request, id):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        id_sesion=id
    )

    movimientos_pendientes = MovimientoInventario.objects.filter(
        sesion=sesion,
        tipo_movimiento="salida",
        devoluciones__isnull=True
    ).exists()

    if movimientos_pendientes:

        messages.error(
            request,
            "No se puede eliminar la sesión porque tiene movimientos de inventario pendientes por devolver."
        )

        return redirect(
            "lista_sesiones",
            id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
        )

    sesion.estado = False
    sesion.save()

    messages.success(
        request,
        "Sesión eliminada correctamente."
    )

    return redirect(
        "lista_sesiones",
        id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
    )

def calendario(request):

    entrenamientos = Entrenamiento.objects.filter(
        estado=True
    )

    categorias = Categoria.objects.filter(
        estado=True
    )

    entrenadores = Usuario.objects.filter(
        roles__rol_usuario__iexact="Entrenador",
        estado=True
    ).distinct()
        
    return render(
        request,
        'sesion_entrenamiento/calendario.html',
        {
            'entrenamientos': entrenamientos,
            'categorias': categorias,
            'entrenadores': entrenadores
        }
    )


def _categoria_jugador_id(usuario_id):
    matriculas = Matricula.objects.filter(
        id_jugador_id=usuario_id,
        estado=True,
    )
    historial = HistorialCategoria.objects.filter(
        id_matricula__in=matriculas,
        estado=True,
    ).first()
    return historial.id_categoria_id if historial else None


def calendario_eventos(request):

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return JsonResponse([], safe=False)

    roles = request.session.get("roles", "")
    es_admin = "Administrador" in roles
    es_entrenador = "Entrenador" in roles and not es_admin
    es_jugador = "Jugador" in roles and not es_admin and not es_entrenador

    entrenamiento = request.GET.get(
        'entrenamiento'
    )

    categoria = request.GET.get(
        'categoria'
    )

    entrenador = request.GET.get(
        'entrenador'
    )

    sesiones = (
        SesionEntrenamiento.objects
        .filter(
            estado=True
        )
        .select_related(
            'id_entrenamiento',
            'id_entrenador'
        )
    )

    if es_entrenador:
        sesiones = sesiones.filter(
            id_entrenador_id=usuario_id,
        )
        if entrenamiento:
            sesiones = sesiones.filter(
                id_entrenamiento_id=entrenamiento,
            )
        if categoria:
            sesiones = sesiones.filter(
                sesioncategoria__id_categoria_id=categoria,
                sesioncategoria__estado=True,
            ).distinct()
    elif es_jugador:
        categoria_jugador = _categoria_jugador_id(usuario_id)
        if categoria_jugador:
            sesiones = sesiones.filter(
                sesioncategoria__id_categoria_id=categoria_jugador,
                sesioncategoria__estado=True,
            ).distinct()
        else:
            sesiones = sesiones.none()
    elif es_admin:
        if entrenamiento:
            sesiones = sesiones.filter(
                id_entrenamiento_id=entrenamiento,
            )

        if entrenador:
            sesiones = sesiones.filter(
                id_entrenador_id=entrenador,
            )

        if categoria:
            sesiones = sesiones.filter(
                sesioncategoria__id_categoria_id=categoria,
                sesioncategoria__estado=True,
            ).distinct()
    else:
        sesiones = sesiones.none()

    eventos = []

    colores = [
        "#1e73be",
        "#28a745",
        "#ffc107",
        "#dc3545",
        "#6f42c1",
        "#17a2b8"
    ]

    for i, sesion in enumerate(sesiones):

        eventos.append({

            "id": sesion.id_sesion,

            "title": (
                sesion.id_entrenamiento.descripcion
                or "Sin descripción"
            ),

            "start": (
                f"{sesion.fecha}T{sesion.hora_inicio}"
            ),

            "end": (
                f"{sesion.fecha}T{sesion.hora_fin}"
            ),

            "backgroundColor":
                colores[i % len(colores)],

            "extendedProps": {

                "entrenador":
                    sesion.id_entrenador.nombre_completo,

                "lugar":
                    sesion.id_entrenamiento.lugar or "",

                "observaciones":
                    sesion.id_entrenamiento.observaciones or "",

                "fecha":
                    str(sesion.fecha),

                "hora_inicio":
                    str(sesion.hora_inicio),

                "hora_fin":
                    str(sesion.hora_fin)
            }
        })

    return JsonResponse(
        eventos,
        safe=False
    )
