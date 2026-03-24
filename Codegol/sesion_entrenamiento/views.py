from django.shortcuts import render, get_object_or_404, redirect
from .models import SesionEntrenamiento
from entrenamientos.models import Entrenamiento
from usuario.models import Usuario, DetallesUsuarioRol
from django.db.models import Q
from datetime import datetime

def lista_sesiones(request, id_entrenamiento):
    entrenamiento = get_object_or_404(
        Entrenamiento,
        id_entrenamiento=id_entrenamiento,
        estado=True
    )

    query = request.GET.get('q', '').strip()

    sesiones = SesionEntrenamiento.objects.filter(
        estado=True,
        id_entrenamiento=entrenamiento
    )

    if query:
        filtros = Q()

        try:
            # 1. Fecha completa: 15/07/2025
            fecha = datetime.strptime(query, "%d/%m/%Y").date()
            filtros |= Q(fecha=fecha)

        except ValueError:
            try:
                # 2. Día/Mes: 15/07
                fecha = datetime.strptime(query, "%d/%m")
                filtros |= Q(fecha__day=fecha.day, fecha__month=fecha.month)

            except ValueError:
                # 3. Solo día: 15
                if query.isdigit():
                    filtros |= Q(fecha__day=int(query))

        # 4. Texto (siempre que haya query)
        filtros |= Q(id_entrenamiento__descripcion__icontains=query)

        sesiones = sesiones.filter(filtros)

    return render(request, 'sesion_entrenamiento/lista.html', {
        'entrenamiento': entrenamiento,
        'sesiones': sesiones,
        'query': query
    })


def crear_sesion(request, id_entrenamiento):
    entrenamiento = get_object_or_404(Entrenamiento, id_entrenamiento=id_entrenamiento)

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    entrenadores = None
    entrenador_seleccionado = None

    # 🔥 PRIORIDAD: ADMIN
    if "Administrador" in roles:
        entrenadores = Usuario.objects.filter(
            roles__rol_usuario="Entrenador"
        )

    # 🔥 SI ES ENTRENADOR
    elif "Entrenador" in roles:
        entrenador_seleccionado = Usuario.objects.get(id_usuario=usuario_id)

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # 🔥 ADMIN selecciona entrenador desde form
        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            entrenador = Usuario.objects.get(id_usuario=entrenador_id)

        # 🔥 ENTRENADOR se asigna automáticamente
        else:
            entrenador = entrenador_seleccionado

        SesionEntrenamiento.objects.create(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=1,
            id_entrenador=entrenador,
            id_entrenamiento=entrenamiento
        )

        return redirect('lista_sesiones', id_entrenamiento=entrenamiento.id_entrenamiento)

    return render(request, "sesion_entrenamiento/crear.html", {
        "entrenamiento": entrenamiento,
        "entrenadores": entrenadores,
        "es_admin": "Administrador" in roles
    })


def editar_sesion(request, id):
    sesion = get_object_or_404(SesionEntrenamiento, pk=id, estado=True)

    # ✅ obtener entrenamiento desde la sesión
    entrenamiento = sesion.id_entrenamiento

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    entrenadores = None
    entrenador_seleccionado = None

    # 🔥 ADMIN puede cambiar entrenador
    if "Administrador" in roles:
        entrenadores = Usuario.objects.filter(
            roles__rol_usuario="Entrenador"
        )

    # 🔥 ENTRENADOR solo se asigna a sí mismo
    elif "Entrenador" in roles:
        entrenador_seleccionado = Usuario.objects.get(id_usuario=usuario_id)

    if request.method == 'POST':
        sesion.fecha = request.POST.get('fecha')
        sesion.hora_inicio = request.POST.get('hora_inicio')
        sesion.hora_fin = request.POST.get('hora_fin')

        # 🔥 ADMIN selecciona entrenador
        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            sesion.id_entrenador = get_object_or_404(Usuario, id_usuario=entrenador_id)

        # 🔥 ENTRENADOR automático
        else:
            sesion.id_entrenador = entrenador_seleccionado

        sesion.save()

        return redirect(
            'lista_sesiones',
            id_entrenamiento=entrenamiento.id_entrenamiento
        )

    return render(request, 'sesion_entrenamiento/editar.html', {
        'sesion': sesion,
        'entrenamiento': entrenamiento,
        'entrenadores': entrenadores,
        'es_admin': "Administrador" in roles
    })


def eliminar_sesion(request, id):
    sesion = get_object_or_404(SesionEntrenamiento, pk=id)
    sesion.estado = False  # 👈 borrado lógico
    sesion.save()

    return redirect('lista_sesiones')
