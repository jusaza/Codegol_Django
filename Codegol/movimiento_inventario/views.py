from django.shortcuts import render, get_object_or_404, redirect
from .models import MovimientoInventario
from inventario.models import Inventario
from django.db.models import Sum
from usuario.models import Usuario
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def lista_movimientos(request, id_inventario):
    inventario = get_object_or_404(
    Inventario,
    pk=id_inventario,
    estado=True
)

    query = request.GET.get('q')

    movimientos = MovimientoInventario.objects.filter(
        inventario=inventario
    ).select_related('usuario').order_by('-fecha')

    # 🔎 búsqueda por tipo o observación
    if query:
        movimientos = movimientos.filter(
            tipo_movimiento__icontains=query
        )

    entradas = MovimientoInventario.objects.filter(
        inventario=inventario,
        tipo_movimiento='entrada'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    salidas = MovimientoInventario.objects.filter(
        inventario=inventario,
        tipo_movimiento='salida'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    devoluciones = MovimientoInventario.objects.filter(
        inventario=inventario,
        tipo_movimiento='devolucion'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    stock_total = entradas - salidas + devoluciones

    return render(request, 'movimiento_inventario/lista.html', {
        'movimientos': movimientos,
        'inventario': inventario,
        'query': query,
        'stock_total': stock_total
    })

def crear_movimiento(request, id_inventario):
    inventario = get_object_or_404(Inventario, pk=id_inventario)

    if request.method == "POST":
        cantidad = request.POST.get("cantidad")
        observaciones = request.POST.get("observaciones")

        usuario_id = request.session.get("usuario_id")

        if usuario_id:
            usuario = Usuario.objects.get(pk=usuario_id)

            MovimientoInventario.objects.create(
                inventario=inventario,
                usuario=usuario,
                tipo_movimiento='entrada',  # 🔥 FORZADO
                cantidad=cantidad,
                observaciones=observaciones
            )

        return redirect('lista_movimientos', id_inventario=inventario.id_inventario)

    return render(request, 'movimiento_inventario/crear.html', {
        'inventario': inventario
    })

def actualizar_observaciones(request):
    if request.method == "POST":
        ids = request.POST.getlist('ids[]')
        observaciones = request.POST.getlist('observaciones[]')

        for i in range(len(ids)):
            try:
                movimiento = MovimientoInventario.objects.get(pk=ids[i])
                movimiento.observaciones = observaciones[i]
                movimiento.save()
            except Exception as e:
                print("Error:", e)

        return JsonResponse({"status": "ok"})
