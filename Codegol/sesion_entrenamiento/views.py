from django.shortcuts import render, get_object_or_404, redirect
from .models import SesionEntrenamiento
from entrenamientos.models import Entrenamiento
from usuario.models import Usuario, DetallesUsuarioRol
from django.db.models import Q
from datetime import datetime
from rendimiento.models import Rendimiento
from categoria.models import Categoria
from matricula.models import HistorialCategoria
from asistencia.models import Asistencia

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
            fecha = datetime.strptime(query, "%d/%m/%Y").date()
            filtros |= Q(fecha=fecha)

        except ValueError:
            try:
                fecha = datetime.strptime(query, "%d/%m")
                filtros |= Q(fecha__day=fecha.day, fecha__month=fecha.month)

            except ValueError:
                if query.isdigit():
                    filtros |= Q(fecha__day=int(query))
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

    if "Administrador" in roles:
        entrenadores = Usuario.objects.filter(
            roles__rol_usuario="Entrenador"
        )
    elif "Entrenador" in roles:
        entrenador_seleccionado = Usuario.objects.get(id_usuario=usuario_id)

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")
        id_categoria = request.POST.get("id_categoria")
        rendimiento_general = request.POST.get("rendimiento_general") == "1"

        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            entrenador = Usuario.objects.get(id_usuario=entrenador_id)
        else:
            entrenador = entrenador_seleccionado

        sesion = SesionEntrenamiento.objects.create(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=1,
            id_entrenador=entrenador,
            id_entrenamiento=entrenamiento
        )

        historiales = HistorialCategoria.objects.filter(
            id_categoria_id=id_categoria,
            estado=True
        )

        for h in historiales:
            matricula = h.id_matricula

            asistencia, creada = Asistencia.objects.get_or_create(
                id_sesion=sesion,
                id_matricula=matricula,
                defaults={
                    "tipo_asistencia": "asiste"
                }
            )

            if not creada:
                asistencia.tipo_asistencia = "asiste"
                asistencia.save()

            rendimiento, creado = Rendimiento.objects.get_or_create(
                id_asistencia=asistencia,
                defaults={
                    "estado": rendimiento_general
                }
            )

            if not creado:
                rendimiento.estado = rendimiento_general
                rendimiento.save()

        return redirect('lista_sesiones', id_entrenamiento=entrenamiento.id_entrenamiento)

    return render(request, "sesion_entrenamiento/crear.html", {
        "entrenamiento": entrenamiento,
        "entrenadores": entrenadores,
        "categorias": Categoria.objects.filter(estado=True),
        "es_admin": "Administrador" in roles
    })


def editar_sesion(request, id):
    sesion = get_object_or_404(SesionEntrenamiento, pk=id, estado=True)

    entrenamiento = sesion.id_entrenamiento

    usuario_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])

    entrenadores = None
    entrenador_seleccionado = None

    if "Administrador" in roles:
        entrenadores = Usuario.objects.filter(
            roles__rol_usuario="Entrenador"
        )

    elif "Entrenador" in roles:
        entrenador_seleccionado = Usuario.objects.get(id_usuario=usuario_id)

    asistencias = Asistencia.objects.filter(id_sesion=sesion)
    rendimiento_general_actual = True  # por defecto

    if asistencias.exists():
        rendimiento = Rendimiento.objects.filter(
            id_asistencia__in=asistencias
        ).first()

        if rendimiento:
            rendimiento_general_actual = rendimiento.estado

    if request.method == 'POST':
        sesion.fecha = request.POST.get('fecha')
        sesion.hora_inicio = request.POST.get('hora_inicio')
        sesion.hora_fin = request.POST.get('hora_fin')

        if "Administrador" in roles:
            entrenador_id = request.POST.get("id_entrenador")
            sesion.id_entrenador = get_object_or_404(
                Usuario,
                id_usuario=entrenador_id
            )
        else:
            sesion.id_entrenador = entrenador_seleccionado

        sesion.save()

        rendimiento_general = request.POST.get("rendimiento_general") == "1"

        for asistencia in asistencias:
            try:
                rendimiento = Rendimiento.objects.get(id_asistencia=asistencia)
                rendimiento.estado = rendimiento_general
                rendimiento.save()
            except Rendimiento.DoesNotExist:
                pass

        return redirect(
            'lista_sesiones',
            id_entrenamiento=entrenamiento.id_entrenamiento
        )

    return render(request, 'sesion_entrenamiento/editar.html', {
        'sesion': sesion,
        'entrenamiento': entrenamiento,
        'entrenadores': entrenadores,
        'es_admin': "Administrador" in roles,
        'modo_editar': True,
        'rendimiento_general_actual': rendimiento_general_actual 
    })


def eliminar_sesion(request, id):
    sesion = get_object_or_404(SesionEntrenamiento, pk=id)
    sesion.estado = False  
    sesion.save()

    return redirect('lista_sesiones')
