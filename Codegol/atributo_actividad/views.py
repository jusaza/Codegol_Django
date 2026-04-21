from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ActividadAtributo
from atributo.models import Atributo
from actividad.models import Actividad

def panel_actividad_atributo(request):

    actividades = Actividad.objects.all()
    atributos = Atributo.objects.all()

    lista = ActividadAtributo.objects.select_related('actividad', 'atributo')

    if request.method == 'POST':

        tipo = request.POST.get('tipo')

        # ================= CREAR ATRIBUTO =================
        if tipo == 'atributo':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')

            Atributo.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )

            messages.success(request, "Atributo creado correctamente")
            return redirect('panel_actividad_atributo')  # 👈 IMPORTANTE

        # ================= ASIGNAR ATRIBUTOS =================
        elif tipo == 'actividad_atributo':

            actividad_id = request.POST.get('actividad')
            atributos_seleccionados = request.POST.getlist('atributos')

            actividad = Actividad.objects.get(id_actividad=actividad_id)

            ActividadAtributo.objects.filter(actividad=actividad).exclude(
                atributo_id__in=atributos_seleccionados
            ).delete()

            for atr_id in atributos_seleccionados:
                peso = request.POST.get(f'peso_{atr_id}') or 1

                ActividadAtributo.objects.update_or_create(
                    actividad=actividad,
                    atributo_id=atr_id,
                    defaults={'peso': peso}
                )

            messages.success(request, "Atributos actualizados correctamente")
            return redirect('panel_actividad_atributo')  # 👈 IMPORTANTE

        # ================= ELIMINAR =================
        elif tipo == 'eliminar':
            id_rel = request.POST.get('id')

            ActividadAtributo.objects.filter(id=id_rel).delete()

            messages.success(request, "Relación eliminada correctamente")
            return redirect('panel_actividad_atributo')  # 👈 IMPORTANTE

# ================= EDITAR ATRIBUTO =================
        elif tipo == 'editar_atributo':
            id_atr = request.POST.get('id')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')

            Atributo.objects.filter(id_atributo=id_atr).update(
                nombre=nombre,
                descripcion=descripcion
            )

            messages.success(request, "Atributo actualizado correctamente")
            return redirect('panel_actividad_atributo')


# ================= ELIMINAR ATRIBUTO =================
        elif tipo == 'eliminar_atributo':
            id_atr = request.POST.get('id')

    # eliminar relaciones
            ActividadAtributo.objects.filter(atributo_id=id_atr).delete()

    # eliminar atributo
            Atributo.objects.filter(id_atributo=id_atr).delete()

            messages.success(request, "Atributo eliminado correctamente")
            return redirect('panel_actividad_atributo')

    # 🔥 elimina también relaciones (importante)
            ActividadAtributo.objects.filter(atributo_id=id_atr).delete()



    # 🔥 SIEMPRE DEFINIR LISTA (CLAVE)
    lista = ActividadAtributo.objects.select_related('actividad', 'atributo')

    # ================= DATOS PARA JS =================
    relaciones = ActividadAtributo.objects.all().values(
        'actividad_id',
        'atributo_id',
        'peso'
    )

    import json
    relaciones_json = json.dumps([
        {
            "actividad": r['actividad_id'],
            "atributo": r['atributo_id'],
            "peso": float(r['peso'])
        }
        for r in relaciones
    ])

    return render(request, 'actividad_atributo/lista_atributo_actividad.html', {
        'actividades': actividades,
        'atributos': atributos,
        'actividad_atributos_json': relaciones_json,
        'lista': lista
    })