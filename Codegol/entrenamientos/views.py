from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Entrenamiento
from entrenamiento_actividad.models import EntrenamientoActividad
from actividad.models import Actividad


def panel_entrenamiento(request):

    entrenamientos = Entrenamiento.objects.all()
    actividades = Actividad.objects.all()
    relaciones = EntrenamientoActividad.objects.select_related('entrenamiento', 'actividad')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        # ================= CREAR ENTRENAMIENTO =================
        if tipo == 'crear_entrenamiento':

            descripcion = request.POST.get(
                'descripcion',
                ''
            ).strip()

            lugar = request.POST.get(
                'lugar',
                ''
            ).strip()

            observaciones = request.POST.get(
                'observaciones',
                ''
            ).strip()

            if len(descripcion) < 5:

                messages.error(
                    request,
                    'La descripción debe tener mínimo 5 caracteres'
                )

                return redirect('panel_entrenamiento')

            if len(lugar) < 3:

                messages.error(
                    request,
                    'El lugar debe tener mínimo 3 caracteres'
                )

                return redirect('panel_entrenamiento')

            if observaciones and len(observaciones) < 10:

                messages.error(
                    request,
                    'Las observaciones deben tener mínimo 10 caracteres'
                )

                return redirect('panel_entrenamiento')

            Entrenamiento.objects.create(
                descripcion=descripcion,
                lugar=lugar,
                estado=True,
                observaciones=observaciones
            )

            messages.success(
                request,
                "Entrenamiento creado"
            )

            return redirect('panel_entrenamiento')

        # ================= EDITAR =================
        elif tipo == 'editar_entrenamiento':

            ent = get_object_or_404(
                Entrenamiento,
                pk=request.POST.get('id')
            )

            descripcion = request.POST.get(
                'descripcion',
                ''
            ).strip()

            lugar = request.POST.get(
                'lugar',
                ''
            ).strip()

            observaciones = request.POST.get(
                'observaciones',
                ''
            ).strip()

            if len(descripcion) < 5:

                messages.error(
                    request,
                    'La descripción debe tener mínimo 5 caracteres'
                )

                return redirect('panel_entrenamiento')

            if len(lugar) < 3:

                messages.error(
                    request,
                    'El lugar debe tener mínimo 3 caracteres'
                )

                return redirect('panel_entrenamiento')

            if observaciones and len(observaciones) < 10:

                messages.error(
                    request,
                    'Las observaciones deben tener mínimo 10 caracteres'
                )

                return redirect('panel_entrenamiento')

            ent.descripcion = descripcion
            ent.lugar = lugar
            ent.observaciones = observaciones

            ent.save()

            messages.success(
                request,
                "Entrenamiento actualizado"
            )

            return redirect('panel_entrenamiento')

        # ================= ELIMINAR =================
        elif tipo == 'eliminar_entrenamiento':
            ent = get_object_or_404(Entrenamiento, pk=request.POST.get('id'))
            ent.delete()

            messages.success(request, "Entrenamiento eliminado")
            return redirect('panel_entrenamiento')

        # ================= ASIGNAR ACTIVIDADES =================
        elif tipo == 'asignar_actividades':

            entrenamiento_id = request.POST.get('entrenamiento')
            actividades_ids = request.POST.getlist('actividades')

            entrenamiento = Entrenamiento.objects.get(id_entrenamiento=entrenamiento_id)

            # eliminar las que ya no están
            EntrenamientoActividad.objects.filter(entrenamiento=entrenamiento).exclude(
                actividad_id__in=actividades_ids
            ).delete()

            # crear o actualizar
            for i, act_id in enumerate(actividades_ids):
                duracion = request.POST.get(f'duracion_{act_id}') or 0

                EntrenamientoActividad.objects.update_or_create(
                    entrenamiento=entrenamiento,
                    actividad_id=act_id,
                    defaults={
                        'orden': i + 1,
                        'duracion_min': duracion
                    }
                )

            messages.success(request, "Actividades asignadas")
            return redirect('panel_entrenamiento')

    return render(request, 'entrenamientos/lista.html', {
        'entrenamientos': entrenamientos,
        'actividades': actividades,
        'relaciones': relaciones
    })