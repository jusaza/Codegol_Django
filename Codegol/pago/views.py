from django.shortcuts import render, get_object_or_404, redirect
from .models import Pago

# LISTAR
def lista_pagos(request):
    query = request.GET.get('q')
    if query:
        pagos = Pago.objects.filter(concepto_pago__icontains=query)
    else:
        pagos = Pago.objects.all()
    return render(request, 'pago/lista.html', {'pagos': pagos, 'query': query})

# CREAR
def crear_pago(request):
    if request.method == 'POST':
        concepto = request.POST.get('concepto_pago')
        fecha = request.POST.get('fecha_pago')
        metodo = request.POST.get('metodo_pago')
        observaciones = request.POST.get('observaciones')
        valor = request.POST.get('valor_total')

        Pago.objects.create(
            concepto_pago=concepto,
            fecha_pago=fecha,
            metodo_pago=metodo,
            observaciones=observaciones,
            valor_total=valor
        )
        return redirect('lista_pagos')

    return render(request, 'pago/crear.html')

# EDITAR
def editar_pago(request, id):
    pago = get_object_or_404(Pago, pk=id)

    if request.method == 'POST':
        pago.concepto_pago = request.POST.get('concepto_pago')
        pago.fecha_pago = request.POST.get('fecha_pago')
        pago.metodo_pago = request.POST.get('metodo_pago')
        pago.observaciones = request.POST.get('observaciones')
        pago.valor_total = request.POST.get('valor_total')
        pago.save()
        return redirect('lista_pagos')

    return render(request, 'pago/editar.html', {'pago': pago})

# ELIMINAR
def eliminar_pago(request, id):
    pago = get_object_or_404(Pago, pk=id)
    pago.estado = False
    pago.save()
    return redirect('lista_pagos')