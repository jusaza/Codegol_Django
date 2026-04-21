from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria


def lista_categoria(request):
    query = request.GET.get('q')

    if query:
        categorias = Categoria.objects.filter(
            nombre_categoria__icontains=query,
            estado=True
        )
    else:
        categorias = Categoria.objects.filter(estado=True)

    return render(request, 'categoria/lista.html', {
        'categorias': categorias,
        'query': query
    })


def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_categoria')

        if nombre:
            Categoria.objects.create(
                nombre_categoria=nombre.strip(),
                estado=True
            )

        return redirect('lista_categoria')

    return render(request, 'categoria/crear.html')


def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_categoria')

        if nombre:
            categoria.nombre_categoria = nombre.strip()
            categoria.save()

        return redirect('lista_categoria')

    return render(request, 'categoria/editar.html', {
        'categoria': categoria
    })


def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)
    categoria.estado = False
    categoria.save()

    return redirect('lista_categoria')

