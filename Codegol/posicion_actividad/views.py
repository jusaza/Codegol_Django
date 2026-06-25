# views.py COMPLETO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import PosicionActividad
from posicion.models import Posicion
from actividad.models import Actividad

import json


# =====================================================
# PANEL PRINCIPAL
# =====================================================
def panel_posicion_actividad(request):

    if request.method == 'POST':

        tipo = request.POST.get('tipo')

        # =================================================
        # CREAR POSICION
        # =================================================
        if tipo == 'posicion':

            nombre = request.POST.get('nombre', '').strip()

            if len(nombre) < 4:

                messages.error(
                    request,
                    'El nombre debe tener mínimo 4 caracteres'
                )

            elif len(nombre) > 20:

                messages.error(
                    request,
                    'El nombre no puede superar 20 caracteres'
                )

            elif Posicion.objects.filter(
                nombre__iexact=nombre
            ).exists():

                messages.error(
                    request,
                    'La posición ya existe'
                )

            else:

                Posicion.objects.create(
                    nombre=nombre.title()
                )

                messages.success(
                    request,
                    'Posición creada correctamente'
                )

            return redirect('panel_posicion_actividad')

        # =================================================
        # CREAR ACTIVIDAD
        # =================================================
        elif tipo == 'actividad':

            nombre = request.POST.get('nombre', '').strip()

            descripcion = request.POST.get(
                'descripcion',
                ''
            ).strip()

            estado = request.POST.get('estado') == 'on'

            if len(nombre) < 2:

                messages.error(
                    request,
                    'El nombre debe tener mínimo 2 caracteres'
                )

            elif len(nombre) > 20:

                messages.error(
                    request,
                    'El nombre no puede superar 20 caracteres'
                )

            elif len(descripcion) < 10:

                messages.error(
                    request,
                    'La descripción debe tener mínimo 10 caracteres'
                )

            elif len(descripcion) > 60:

                messages.error(
                    request,
                    'La descripción no puede superar 60 caracteres'
                )

            elif Actividad.objects.filter(
                nombre__iexact=nombre
            ).exists():

                messages.error(
                    request,
                    'La actividad ya existe'
                )

            else:

                Actividad.objects.create(
                    nombre=nombre.title(),
                    descripcion=descripcion,
                    estado=estado
                )

                messages.success(
                    request,
                    'Actividad creada correctamente'
                )

            return redirect('panel_posicion_actividad')

        # =================================================
        # RELACION
        # =================================================
        elif tipo == 'relacion':

            posicion_id = request.POST.get('posicion')

            obligatorio = (
                request.POST.get('obligatorio') == 'on'
            )

            posicion = get_object_or_404(
                Posicion,
                id_posicion=posicion_id
            )

            actividades_ids = request.POST.getlist(
                'actividades'
            )

            actividades_ids = [
                int(a)
                for a in actividades_ids
            ]

            actuales = PosicionActividad.objects.filter(
                posicion=posicion
            )

            actuales_ids = [
                r.actividad.id_actividad
                for r in actuales
            ]

            # CREAR
            for act_id in actividades_ids:

                if act_id not in actuales_ids:

                    PosicionActividad.objects.create(
                        posicion=posicion,
                        actividad_id=act_id,
                        obligatorio=obligatorio
                    )

            # ELIMINAR
            for r in actuales:

                if r.actividad.id_actividad not in actividades_ids:

                    r.delete()

            # ACTUALIZAR
            PosicionActividad.objects.filter(
                posicion=posicion,
                actividad_id__in=actividades_ids
            ).update(
                obligatorio=obligatorio
            )

            messages.success(
                request,
                'Actividades sincronizadas correctamente'
            )

            return redirect('panel_posicion_actividad')

    # =====================================================
    # CONSULTAS
    # =====================================================
    relaciones = PosicionActividad.objects.select_related(
        'posicion',
        'actividad'
    )

    posiciones = Posicion.objects.all().order_by(
        'nombre'
    )

    actividades = Actividad.objects.all().order_by(
        'nombre'
    )

    relaciones_json = json.dumps([
        {
            'posicion': r.posicion.id_posicion,
            'actividad': r.actividad.id_actividad
        }
        for r in relaciones
    ])

    return render(
        request,
        'posicion_actividad/lista_posicion_actividad.html',
        {
            'relaciones': relaciones,
            'posiciones': posiciones,
            'actividades': actividades,
            'relaciones_json': relaciones_json
        }
    )


# =====================================================
# EDITAR POSICION
# =====================================================
def editar_posicion(request, id):

    posicion = get_object_or_404(
        Posicion,
        id_posicion=id
    )

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        if len(nombre) < 4:

            messages.error(
                request,
                'El nombre debe tener mínimo 4 caracteres'
            )

        elif len(nombre) > 20:

            messages.error(
                request,
                'El nombre no puede superar 20 caracteres'
            )

        elif Posicion.objects.filter(
            nombre__iexact=nombre
        ).exclude(
            id_posicion=id
        ).exists():

            messages.error(
                request,
                'Ya existe esa posición'
            )

        else:

            posicion.nombre = nombre.title()

            posicion.save()

            messages.success(
                request,
                'Posición actualizada correctamente'
            )

    return redirect('panel_posicion_actividad')


# =====================================================
# EDITAR ACTIVIDAD
# =====================================================
def editar_actividad(request, id):

    actividad = get_object_or_404(
        Actividad,
        id_actividad=id
    )

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        estado = request.POST.get('estado') == 'on'

        if len(nombre) < 2:

            messages.error(
                request,
                'El nombre debe tener mínimo 2 caracteres'
            )

        elif len(nombre) > 20:

            messages.error(
                request,
                'El nombre no puede superar 20 caracteres'
            )

        elif len(descripcion) < 10:

            messages.error(
                request,
                'La descripción debe tener mínimo 10 caracteres'
            )

        elif len(descripcion) > 60:

            messages.error(
                request,
                'La descripción no puede superar 60 caracteres'
            )

        elif Actividad.objects.filter(
            nombre__iexact=nombre
        ).exclude(
            id_actividad=id
        ).exists():

            messages.error(
                request,
                'Ya existe esa actividad'
            )

        else:

            actividad.nombre = nombre.title()

            actividad.descripcion = descripcion

            actividad.estado = estado

            actividad.save()

            messages.success(
                request,
                'Actividad actualizada correctamente'
            )

    return redirect('panel_posicion_actividad')


# =====================================================
# ELIMINAR POSICION
# =====================================================
def eliminar_posicion(request, id):

    posicion = get_object_or_404(
        Posicion,
        id_posicion=id
    )

    posicion.delete()

    messages.success(
        request,
        'Posición eliminada correctamente'
    )

    return redirect('panel_posicion_actividad')


# =====================================================
# ELIMINAR ACTIVIDAD
# =====================================================
def eliminar_actividad(request, id):

    actividad = get_object_or_404(
        Actividad,
        id_actividad=id
    )

    actividad.delete()

    messages.success(
        request,
        'Actividad eliminada correctamente'
    )

    return redirect('panel_posicion_actividad')


# =====================================================
# ELIMINAR RELACION
# =====================================================
def eliminar_relacion(request, id):

    relacion = get_object_or_404(
        PosicionActividad,
        id=id
    )

    relacion.delete()

    messages.success(
        request,
        'Relación eliminada correctamente'
    )

    return redirect('panel_posicion_actividad')

# =====================================================
# LISTA ACTIVIDADES
# =====================================================
def lista_actividades(request):

    actividades = Actividad.objects.all().order_by(
        'nombre'
    )

    return render(
        request,
        'posicion_actividad/lista_actividades.html',
        {
            'actividades': actividades
        }
    )

# =====================================================
# CREAR ACTIVIDAD DESDE LISTA ACTIVIDADES
# =====================================================
def crear_actividad(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre', '').strip()

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        estado = request.POST.get('estado') == 'on'

        if len(nombre) < 2:

            messages.error(
                request,
                'El nombre debe tener mínimo 2 caracteres'
            )

        elif len(nombre) > 20:

            messages.error(
                request,
                'El nombre no puede superar 20 caracteres'
            )

        elif len(descripcion) < 10:

            messages.error(
                request,
                'La descripción debe tener mínimo 10 caracteres'
            )

        elif len(descripcion) > 60:

            messages.error(
                request,
                'La descripción no puede superar 60 caracteres'
            )

        elif Actividad.objects.filter(
            nombre__iexact=nombre
        ).exists():

            messages.error(
                request,
                'La actividad ya existe'
            )

        else:

            Actividad.objects.create(
                nombre=nombre.title(),
                descripcion=descripcion,
                estado=estado
            )

            messages.success(
                request,
                'Actividad creada correctamente'
            )

    return redirect('lista_actividades')

# =====================================================
# EDITAR ACTIVIDAD LISTA
# =====================================================
def editar_actividad_lista(request, id):

    actividad = get_object_or_404(
        Actividad,
        id_actividad=id
    )

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        estado = request.POST.get('estado') == 'on'

        if len(nombre) < 2:

            messages.error(
                request,
                'El nombre debe tener mínimo 2 caracteres'
            )

        elif len(nombre) > 20:

            messages.error(
                request,
                'El nombre no puede superar 20 caracteres'
            )

        elif len(descripcion) < 10:

            messages.error(
                request,
                'La descripción debe tener mínimo 10 caracteres'
            )

        elif len(descripcion) > 60:

            messages.error(
                request,
                'La descripción no puede superar 60 caracteres'
            )

        elif Actividad.objects.filter(
            nombre__iexact=nombre
        ).exclude(
            id_actividad=id
        ).exists():

            messages.error(
                request,
                'Ya existe esa actividad'
            )

        else:

            actividad.nombre = nombre.title()

            actividad.descripcion = descripcion

            actividad.estado = estado

            actividad.save()

            messages.success(
                request,
                'Actividad actualizada correctamente'
            )

    return redirect('lista_actividades')

# =====================================================
# ELIMINAR ACTIVIDAD LISTA
# =====================================================
def eliminar_actividad_lista(request, id):

    actividad = get_object_or_404(
        Actividad,
        id_actividad=id
    )

    actividad.delete()

    messages.success(
        request,
        'Actividad eliminada correctamente'
    )

    return redirect('lista_actividades')