from django.shortcuts import render, get_object_or_404, redirect
from .models import SesionEntrenamiento
from entrenamientos.models import Entrenamiento
from usuario.models import Usuario
from categoria.models import Categoria
from matricula.models import HistorialCategoria
from asistencia.models import Asistencia
from sesion_categoria.models import SesionCategoria
from entrenamiento_actividad.models import EntrenamientoActividad
from sesion_actividad.models import SesionActividad
from django.db.models import Q


# ================= LISTAR =================
def lista_sesiones(request, id_entrenamiento):

    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento
    )

    sesiones = SesionEntrenamiento.objects.filter(
        id_entrenamiento=entrenamiento,
        estado=True
    ).select_related(
        'id_entrenador'
    ).order_by(
        '-fecha'
    )

    # 🔥 entrenadores correctos
    entrenadores = Usuario.objects.filter(
        usuario__id_rol__rol_usuario__iexact="Entrenador"
    ).distinct()

    for sesion in sesiones:

        sesion.categorias_registradas = (
            SesionCategoria.objects
            .filter(
                id_sesion=sesion,
                estado=True
            )
            .select_related(
                'id_categoria'
            )
        )
    
        for categoria in sesion.categorias_registradas:

            asistencias = Asistencia.objects.filter(
                id_sesion=sesion,
                id_categoria=categoria.id_categoria
            )

            pendientes = asistencias.filter(
                Q(tipo_asistencia__isnull=True) |
                Q(tipo_asistencia='')
            ).exists()

            print(
                categoria.id_categoria.nombre_categoria,
                asistencias.count(),
                pendientes
            )

            categoria.asistencia_completa = not pendientes


    return render(
        request,
        "sesion_entrenamiento/lista.html",
        {
            "entrenamiento": entrenamiento,
            "sesiones": sesiones,
            "entrenadores": entrenadores,
            "categorias": Categoria.objects.filter(
                estado=True
            )
        }
    )


# ================= CREAR =================
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
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        categorias = request.POST.getlist("categorias[]")

        # ================= ENTRENADOR =================

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

        # ================= CREAR SESIÓN =================

        sesion = SesionEntrenamiento.objects.create(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=True,
            id_entrenador=entrenador,
            id_entrenamiento=entrenamiento
        )

        # =====================================
        # CONGELAR ACTIVIDADES DEL ENTRENAMIENTO
        # =====================================

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
        "sesion_entrenamiento/form.html",
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

    sesion.estado = False
    sesion.save()

    return redirect(
        'lista_sesiones',
        id_entrenamiento=sesion.id_entrenamiento.id_entrenamiento
    )