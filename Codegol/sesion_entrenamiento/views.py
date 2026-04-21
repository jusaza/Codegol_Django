from django.shortcuts import render, get_object_or_404, redirect
from .models import SesionEntrenamiento
from entrenamientos.models import Entrenamiento
from usuario.models import Usuario
from categoria.models import Categoria
from matricula.models import HistorialCategoria
from asistencia.models import Asistencia


# ================= LISTAR =================
def lista_sesiones(request, id_entrenamiento):

    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento
    )

    sesiones = SesionEntrenamiento.objects.filter(
        id_entrenamiento=entrenamiento,
        estado=True
    ).select_related('id_entrenador')

    # 🔥 entrenadores correctos
    entrenadores = Usuario.objects.filter(
        usuario__id_rol__rol_usuario__iexact="Entrenador"
    ).distinct()

    return render(request, "sesion_entrenamiento/lista.html", {
        "entrenamiento": entrenamiento,
        "sesiones": sesiones,
        "entrenadores": entrenadores,
        "categorias": Categoria.objects.filter(estado=True)
    })


# ================= CREAR =================
def crear_sesion(request, id_entrenamiento):

    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento
    )

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    # 🔥 entrenadores
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
        id_categoria = request.POST.get("id_categoria")

        # 🔥 definir entrenador
        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            entrenador = get_object_or_404(
                Usuario,
                id_usuario=entrenador_id
            )
        else:
            entrenador = entrenador_seleccionado

        # 🔥 crear sesión
        sesion = SesionEntrenamiento.objects.create(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=True,
            id_entrenador=entrenador,
            id_entrenamiento=entrenamiento
        )

        # 🔥 asistencia automática (filtro lógico por categoría)
        if id_categoria:
            historiales = HistorialCategoria.objects.filter(
                id_categoria_id=id_categoria,
                estado=True
            )

            for h in historiales:
                Asistencia.objects.get_or_create(
                    id_sesion=sesion,
                    id_matricula=h.id_matricula,
                    defaults={"tipo_asistencia": "asiste"}
                )

        return redirect(
            'lista_sesiones',
            id_entrenamiento=id_entrenamiento
        )

    return render(request, "sesion_entrenamiento/lista.html", {
        "entrenamiento": entrenamiento,
        "entrenadores": entrenadores,
        "categorias": Categoria.objects.filter(estado=True),
        "es_admin": "Administrador" in roles
    })


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

        sesion.fecha = request.POST.get('fecha')
        sesion.hora_inicio = request.POST.get('hora_inicio')
        sesion.hora_fin = request.POST.get('hora_fin')

        # 🔥 actualizar entrenador
        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            sesion.id_entrenador = get_object_or_404(
                Usuario,
                id_usuario=entrenador_id
            )
        else:
            sesion.id_entrenador = entrenador_seleccionado

        sesion.save()

        return redirect(
            'lista_sesiones',
            id_entrenamiento=entrenamiento.id_entrenamiento
        )

    return render(request, 'sesion_entrenamiento/form.html', {
        'sesion': sesion,
        'entrenamiento': entrenamiento,
        'entrenadores': entrenadores,
        'es_admin': "Administrador" in roles
    })


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