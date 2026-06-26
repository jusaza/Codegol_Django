from django.shortcuts import render, get_object_or_404, redirect
from .models import MovimientoInventario
from inventario.models import Inventario
from django.db.models import Sum, Q
from usuario.models import Usuario
from django.http import JsonResponse
import unicodedata
from django.http import HttpResponse
from sesion_entrenamiento.models import SesionEntrenamiento

def limpiar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()


def lista_movimientos(request, id_inventario):
    inventario = get_object_or_404(
        Inventario,
        pk=id_inventario,
        estado=True
    )

    query = request.GET.get('q')

    movimientos = MovimientoInventario.objects.filter(
        inventario=inventario
    ).select_related('usuario').prefetch_related('devoluciones').order_by('-fecha')

    solo_devoluciones = False

    if query:
        query_limpio = limpiar_texto(query)

        # 🔥 detectar devoluciones (incluye parcial / total)
        if any(p in query_limpio for p in ['devolucion', 'devuelto', 'parcial', 'total']):
            solo_devoluciones = True
            movimientos = movimientos.filter(tipo_movimiento='devolucion')
        else:
            movimientos = movimientos.filter(
                Q(tipo_movimiento__icontains=query_limpio) |
                Q(observaciones__icontains=query)
            )

    # 🔥 evitar duplicados (ocultar devoluciones normales)
    if not solo_devoluciones:
        movimientos = movimientos.exclude(tipo_movimiento='devolucion')

    # 📊 STOCK
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
        'stock_total': stock_total,
        'solo_devoluciones': solo_devoluciones
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
                tipo_movimiento='entrada',  # 🔥 por ahora solo entrada
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
            movimiento = MovimientoInventario.objects.get(pk=ids[i])
            nueva_obs = observaciones[i].strip()

            if movimiento.movimiento_padre:
                total_devuelto = movimiento.movimiento_padre.devoluciones.aggregate(
                    total=Sum('cantidad')
                )['total'] or 0

                restante = movimiento.movimiento_padre.cantidad - total_devuelto

                estado = "devuelto" if restante == 0 else (
                    "parcial" if total_devuelto > 0 else "pendiente"
                )

                if estado in ["pendiente", "parcial"] and nueva_obs == "":
                    return JsonResponse({
                        "error": "No puedes dejar observación vacía en devoluciones activas"
                    }, status=400)

            movimiento.observaciones = nueva_obs
            movimiento.save()

        return JsonResponse({"status": "ok"})


#Salidas

def salidas_sesion(request, id_sesion):

    sesion = get_object_or_404(
        SesionEntrenamiento,
        pk=id_sesion,
        estado=True
    )

    inventarios = Inventario.objects.filter(estado=True)
    query = request.GET.get('q')

    movimientos = MovimientoInventario.objects.filter(
        sesion=sesion,
        tipo_movimiento='salida',
    ).select_related('usuario', 'inventario')\
     .prefetch_related('devoluciones')\
     .order_by('-fecha')

    # 🔥 STOCK INVENTARIOS
    for inv in inventarios:
        entradas = MovimientoInventario.objects.filter(
            inventario=inv, tipo_movimiento='entrada'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        salidas = MovimientoInventario.objects.filter(
            inventario=inv, tipo_movimiento='salida'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        devoluciones = MovimientoInventario.objects.filter(
            inventario=inv, tipo_movimiento='devolucion'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        inv.stock = entradas - salidas + devoluciones

    # 🔥 ESTADO DE SALIDAS (CLAVE 🔥)
    for m in movimientos:
        total_devuelto = m.devoluciones.aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        m.restante = m.cantidad - total_devuelto

        if m.restante == 0:
            m.estado = "devuelto"
        elif total_devuelto > 0:
            m.estado = "parcial"
        else:
            m.estado = "pendiente"

    # 🔥 CREAR SALIDA
    if request.method == "POST":
        inventario_id = request.POST.get("inventario_id")
        cantidad = int(request.POST.get("cantidad"))
        observaciones = request.POST.get("observaciones")

        usuario = Usuario.objects.get(pk=request.session.get("usuario_id"))
        inventario = Inventario.objects.get(pk=inventario_id)

        entradas = MovimientoInventario.objects.filter(
            inventario=inventario, tipo_movimiento='entrada'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        salidas = MovimientoInventario.objects.filter(
            inventario=inventario, tipo_movimiento='salida'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        devoluciones = MovimientoInventario.objects.filter(
            inventario=inventario, tipo_movimiento='devolucion'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        stock_actual = entradas - salidas + devoluciones

        if cantidad < 1:
            return HttpResponse("Cantidad inválida")

        if cantidad > stock_actual:
            return HttpResponse("No hay suficiente stock")

        MovimientoInventario.objects.create(
            inventario=inventario,
            usuario=usuario,
            sesion=sesion,
            tipo_movimiento='salida',
            cantidad=cantidad,
            observaciones=observaciones
        )

        return redirect('salidas_sesion', id_sesion=id_sesion)

    return render(request, 'movimiento_inventario/salidas.html', {
        'sesion': sesion,
        'movimientos': movimientos,
        'inventarios': inventarios,
        'query': query,
    })


def crear_devolucion(request, id_movimiento):
    salida = get_object_or_404(MovimientoInventario, pk=id_movimiento)

    total_devuelto = salida.devoluciones.aggregate(
        total=Sum('cantidad')
    )['total'] or 0

    restante = salida.cantidad - total_devuelto

    if restante <= 0:
        return HttpResponse("Este movimiento ya fue devuelto completamente")

    if request.method == "POST":
        try:
            cantidad = int(request.POST.get("cantidad"))
        except:
            return HttpResponse("Cantidad inválida")

        observaciones = request.POST.get("observaciones")

        if cantidad < 1:
            return HttpResponse("La cantidad debe ser mayor a 0")

        if cantidad > restante:
            return HttpResponse("Excede lo prestado")

        if cantidad < restante and not observaciones:
            return HttpResponse("Debe explicar por qué la devolución es parcial (faltantes).")

        usuario = Usuario.objects.get(pk=request.session.get("usuario_id"))

        MovimientoInventario.objects.create(
            inventario=salida.inventario,
            usuario=usuario,
            sesion=salida.sesion,
            tipo_movimiento='devolucion',
            cantidad=cantidad,
            movimiento_padre=salida,
            observaciones=observaciones
        )

        return redirect(
            'salidas_sesion',
            id_sesion=salida.sesion.id_sesion
        )

    return render(request, 'movimiento_inventario/devolver.html', {
        'salida': salida,
        'total_devuelto': total_devuelto,
        'restante': restante
    })
