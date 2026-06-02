from django.shortcuts import render
from .models import Inventario
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
def lista_inventario(request):
    query = request.GET.get('q')

    if query:
        inventarios = Inventario.objects.filter(
            nombre_articulo__icontains=query,
            estado=True
        )
    else:
        inventarios = Inventario.objects.filter(estado=True)

    return render(request, 'inventario/lista.html', {
        'inventarios': inventarios,
        'query': query
    })


def crear_inventario(request):
    if request.method == 'POST':
        Inventario.objects.create(
            nombre_articulo=request.POST.get('nombre_articulo'),
            descripcion=request.POST.get('descripcion'),
            estado=True
        )
        return redirect('lista_inventario')

    return render(request, 'inventario/form.html')


def editar_inventario(request, id):
    inventario = get_object_or_404(Inventario, pk=id)

    if request.method == 'POST':
        inventario.nombre_articulo = request.POST.get('nombre_articulo')
        inventario.descripcion = request.POST.get('descripcion')
        inventario.save()

        return redirect('lista_inventario')

    return render(request, 'inventario/form.html', {
        'inventario': inventario
    })


def eliminar_inventario(request, id):
    inventario = get_object_or_404(Inventario, pk=id)
    inventario.estado = False
    inventario.save()

    return redirect('lista_inventario')
