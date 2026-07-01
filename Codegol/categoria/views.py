from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria
from django.core.paginator import Paginator


def lista_categoria(request):
    query = request.GET.get('q')

    categorias = Categoria.objects.filter(
        estado=True
    ).order_by('id_categoria')

    if query:
        categorias = categorias.filter(
            nombre_categoria__icontains=query
        )

    paginator = Paginator(categorias, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(request, 'categoria/lista.html', {
        'categorias': page_obj,
        'query': query,
        'page_obj': page_obj
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

    return render(request, 'categoria/form.html')


def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_categoria')

        if nombre:
            categoria.nombre_categoria = nombre.strip()
            categoria.save()

        return redirect('lista_categoria')

    return render(request, 'categoria/form.html', {
        'categoria': categoria
    })


def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id_categoria=id)
    categoria.estado = False
    categoria.save()

    return redirect('lista_categoria')

