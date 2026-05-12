from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PosicionActividad
from posicion.models import Posicion
from actividad.models import Actividad
import json


def panel_posicion_actividad(request):

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        # 🔹 CREAR POSICION
        if tipo == 'posicion':
            nombre = request.POST.get('nombre')

            if Posicion.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, 'La posición ya existe')
            else:
                Posicion.objects.create(nombre=nombre.strip().title())
                messages.success(request, 'Posición creada')

        # 🔹 CREAR ACTIVIDAD
        elif tipo == 'actividad':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')

            if Actividad.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, 'La actividad ya existe')
            else:
                Actividad.objects.create(
                    nombre=nombre.strip().title(),
                    descripcion=descripcion
                )
                messages.success(request, 'Actividad creada')

        # 🔹 CREAR RELACION
        elif tipo == 'relacion':
            posicion_id = request.POST.get('posicion')
            obligatorio = request.POST.get('obligatorio') == 'on'

            posicion = get_object_or_404(Posicion, id_posicion=posicion_id)

    # 🔹 lo que viene del formulario
            actividades_ids = request.POST.getlist('actividades')
            actividades_ids = [int(a) for a in actividades_ids]

    # 🔹 lo que ya existe en BD
            actuales = PosicionActividad.objects.filter(posicion=posicion)
            actuales_ids = [r.actividad.id_actividad for r in actuales]

    # ===============================
    # ➕ CREAR NUEVAS
    # ===============================
            for act_id in actividades_ids:
                if act_id not in actuales_ids:
                    PosicionActividad.objects.create(
                        posicion=posicion,
                        actividad_id=act_id,
                        obligatorio=obligatorio
                    )

    # ===============================
    # ❌ ELIMINAR LAS DESMARCADAS
    # ===============================
            for r in actuales:
                if r.actividad.id_actividad not in actividades_ids:
                    r.delete()

    # ===============================
    # 🔄 ACTUALIZAR OBLIGATORIO
    # ===============================
                PosicionActividad.objects.filter(
                    posicion=posicion,
                    actividad_id__in=actividades_ids
                ).update(obligatorio=obligatorio)

    messages.success(request, 'Actividades sincronizadas correctamente')
    relaciones = PosicionActividad.objects.select_related('posicion', 'actividad')
    posiciones = Posicion.objects.all().order_by('nombre')
    actividades = Actividad.objects.all().order_by('nombre')

    # 🔥 JSON PARA JS
    relaciones_json = json.dumps([
        {
            'posicion': r.posicion.id_posicion,
            'actividad': r.actividad.id_actividad
        } for r in relaciones
    ])

    actividades_json = json.dumps([
        {
            'id': a.id_actividad,
            'nombre': a.nombre
        } for a in actividades
    ])

    return render(request, 'posicion_actividad/lista_posicion_actividad.html', {
        'relaciones': relaciones,
        'posiciones': posiciones,
        'actividades': actividades,
        'relaciones_json': relaciones_json,
        'actividades_json': actividades_json
    })


# 🔹 EDITAR POSICION
def editar_posicion(request, id):
    posicion = get_object_or_404(Posicion, id_posicion=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')

        if Posicion.objects.filter(nombre__iexact=nombre).exclude(id_posicion=id).exists():
            messages.error(request, 'Ya existe esa posición')
        else:
            posicion.nombre = nombre.strip().title()
            posicion.save()
            messages.success(request, 'Posición actualizada')

    return redirect('panel_posicion_actividad')

# 🔹 EDITAR ACTIVIDAD
def editar_actividad(request, id):
    actividad = get_object_or_404(Actividad, id_actividad=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        if Actividad.objects.filter(nombre__iexact=nombre).exclude(id_actividad=id).exists():
            messages.error(request, 'Ya existe esa actividad')
        else:
            actividad.nombre = nombre.strip().title()
            actividad.descripcion = descripcion
            actividad.save()
            messages.success(request, 'Actividad actualizada')

    return redirect('panel_posicion_actividad')


# 🔹 ELIMINAR POSICION
def eliminar_posicion(request, id):
    posicion = get_object_or_404(Posicion, id_posicion=id)
    posicion.delete()
    messages.success(request, 'Posición eliminada')
    return redirect('panel_posicion_actividad')


# 🔹 CAMBIAR OBLIGATORIO
def toggle_obligatorio(request, id):
    relacion = get_object_or_404(PosicionActividad, id=id)
    relacion.obligatorio = not relacion.obligatorio
    relacion.save()
    return redirect('panel_posicion_actividad')


# 🔹 ELIMINAR RELACION
def eliminar_relacion(request, id):
    relacion = get_object_or_404(PosicionActividad, id=id)
    relacion.delete()
    messages.success(request, 'Relación eliminada')
    return redirect('panel_posicion_actividad')