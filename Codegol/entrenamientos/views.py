from django.shortcuts import render, get_object_or_404, redirect
from .models import Entrenamiento

def lista_entrenamientos(request):
    query = request.GET.get('q')

    if query:
        entrenamientos = Entrenamiento.objects.filter(
            descripcion__icontains=query,
            estado=True
        )
    else:
        entrenamientos = Entrenamiento.objects.filter(estado=True)

    return render(request, 'entrenamientos/lista.html', {
        'entrenamientos': entrenamientos,
        'query': query
    })



def crear_entrenamiento(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        lugar = request.POST.get('lugar')
        observaciones = request.POST.get('observaciones')

        Entrenamiento.objects.create(
            descripcion=descripcion,
            estado=True, 
            lugar=lugar,
            observaciones=observaciones
        )

        return redirect('lista_entrenamientos')

    return render(request, 'entrenamientos/crear.html')


def editar_entrenamiento(request, id):
    entrenamiento = get_object_or_404(Entrenamiento, pk=id)

    if request.method == 'POST':
        entrenamiento.descripcion = request.POST.get('descripcion')
        entrenamiento.lugar = request.POST.get('lugar')
        entrenamiento.observaciones = request.POST.get('observaciones')
        entrenamiento.save()

        return redirect('lista_entrenamientos')

    return render(request, 'entrenamientos/editar.html', {
        'entrenamiento': entrenamiento
    })


def eliminar_entrenamiento(request, id):
    entrenamiento = get_object_or_404(Entrenamiento, pk=id)
    entrenamiento.estado = False
    entrenamiento.save()

    return redirect('lista_entrenamientos')
