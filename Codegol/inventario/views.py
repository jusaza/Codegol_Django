from django.shortcuts import render
from .models import Inventario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from movimiento_inventario.models import MovimientoInventario
from django.core.paginator import Paginator
# Create your views here.
def lista_inventario(request):
    query = request.GET.get('q')

    if query:
        inventarios = Inventario.objects.filter(
            nombre_articulo__icontains=query,
            estado=True
        ).order_by('id_inventario')
    else:
        inventarios = Inventario.objects.filter(
            estado=True
        ).order_by('id_inventario')

    paginator = Paginator(inventarios, 10)   # 10 registros por página

    page_number = request.GET.get('page')
    inventarios = paginator.get_page(page_number)

    return render(request, 'inventario/lista.html', {
        'inventarios': inventarios,
        'query': query,
        'modo_inactivos': False
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

    inventario = get_object_or_404(
        Inventario,
        pk=id
    )

    salidas_pendientes = MovimientoInventario.objects.filter(
        inventario=inventario,
        tipo_movimiento='salida',
        devoluciones__isnull=True
    ).exists()

    if salidas_pendientes:

        messages.error(
            request,
            'No se puede desactivar el artículo porque tiene salidas pendientes por devolver.'
        )

        return redirect('lista_inventario')

    inventario.estado = False
    inventario.save()

    messages.success(
        request,
        'Artículo desactivado correctamente.'
    )

    return redirect('lista_inventario')

def lista_inventario_inactivos(request):

    query = request.GET.get('q')

    inventarios = Inventario.objects.filter(
        estado=False
    ).order_by('id_inventario')

    if query:
        inventarios = inventarios.filter(
            nombre_articulo__icontains=query
        )

    paginator = Paginator(inventarios, 10)

    page_number = request.GET.get('page')
    inventarios = paginator.get_page(page_number)

    return render(
        request,
        'inventario/lista.html',
        {
            'inventarios': inventarios,
            'query': query,
            'modo_inactivos': True
        }
    )

def activar_inventario(request, id):

    inventario = get_object_or_404(
        Inventario,
        pk=id
    )

    inventario.estado = True

    inventario.save()

    return redirect(
        'lista_inventario_inactivos'
    )
