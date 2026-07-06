from django.shortcuts import render, get_object_or_404, redirect
from .models import Pago
from usuario.models import DetallesUsuarioRol
from matricula.models import Matricula
from django.db.models import Max
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from django.db.models import Sum
from django.core.paginator import Paginator

# LISTAR
def lista_pagos(request):

    query = request.GET.get('q')
    usuario_id = request.session.get("usuario_id")

    es_jugador = DetallesUsuarioRol.objects.filter(
        id_usuario_id=usuario_id,
        id_rol__rol_usuario__iexact="Jugador"
    ).exists()

    if es_jugador:

        pagos = Pago.objects.filter(
            id_matricula__id_jugador__id_usuario=usuario_id
        ).select_related(
            'id_matricula__id_jugador'
        )

    else:

        pagos = Pago.objects.all().select_related(
            'id_matricula__id_jugador'
        )

    if query:

        pagos = pagos.filter(
            concepto_pago__icontains=query
        )

    # ===========================
    # PAGINACIÓN
    # ===========================

    paginator = Paginator(
        pagos.order_by("-id"),
        10
    )

    page_number = request.GET.get("page")

    pagos = paginator.get_page(
        page_number
    )

    return render(
        request,
        "pago/lista.html",
        {
            "pagos": pagos,
            "query": query
        }
    )

# CREAR
def crear_pago(request):

    # 🔹 Obtener última matrícula activa por usuario
    matriculas = Matricula.objects.filter(
        estado=True,
        id_jugador__estado=True
    ).values('id_jugador').annotate(
        ultima_fecha=Max('fecha_matricula')
    )

    # 🔹 Obtener esas matrículas completas
    matriculas_finales = Matricula.objects.filter(
        estado=True,
        fecha_matricula__in=[m['ultima_fecha'] for m in matriculas]
    ).select_related('id_jugador')

    if request.method == 'POST':
        concepto = request.POST.get('concepto_pago')
        fecha = request.POST.get('fecha_pago')
        metodo = request.POST.get('metodo_pago')
        observaciones = request.POST.get('observaciones')
        valor = request.POST.get('valor_total')
        id_matricula = request.POST.get('id_matricula')

        Pago.objects.create(
            concepto_pago=concepto,
            fecha_pago=fecha,
            metodo_pago=metodo,
            observaciones=observaciones,
            valor_total=valor,
            id_matricula_id=id_matricula  # 🔥 importante
        )
        return redirect('lista_pagos')

    return render(request, 'pago/formulario.html', {
        'metodos': Pago.METODOS,
        'conceptos': Pago.CONCEPTOS,
        'matriculas': matriculas_finales
    })

def editar_pago(request, id):
    pago = get_object_or_404(Pago, pk=id)

    # 🔹 mismas matrículas que en crear
    matriculas = Matricula.objects.filter(
        estado=True,
        id_jugador__estado=True
    ).values('id_jugador').annotate(
        ultima_fecha=Max('fecha_matricula')
    )

    matriculas_finales = Matricula.objects.filter(
        estado=True,
        fecha_matricula__in=[m['ultima_fecha'] for m in matriculas]
    ).select_related('id_jugador')

    if request.method == 'POST':
        pago.concepto_pago = request.POST.get('concepto_pago')
        pago.fecha_pago = request.POST.get('fecha_pago')
        pago.metodo_pago = request.POST.get('metodo_pago')
        pago.observaciones = request.POST.get('observaciones')
        pago.valor_total = request.POST.get('valor_total')
        pago.id_matricula_id = request.POST.get('id_matricula')  
        pago.save()

        return redirect('lista_pagos')

    return render(request, 'pago/formulario.html', {
        'pago': pago,
        'metodos': Pago.METODOS,
        'conceptos': Pago.CONCEPTOS,
        'matriculas': matriculas_finales
    })

# ELIMINAR
def cancelar_pago(request, id):
    pago = Pago.objects.get(id=id)
    
    # Cambiar estado (toggle)
    pago.cancelado = not pago.cancelado
    pago.save()

    return redirect('lista_pagos')

def reporte_pagos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_pagos.pdf"'

    p = canvas.Canvas(response)

    # Título
    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, 800, "Reporte General de Pagos")

    # Fecha actual
    p.setFont("Helvetica", 10)
    p.drawString(50, 780, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")

    # Total recaudado
    total = Pago.objects.filter(cancelado=False).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    p.drawString(50, 760, f"Total recaudado: ${total}")

    pagos = Pago.objects.filter(cancelado=False)

    y = 730

    # Encabezados
    p.setFont("Helvetica-Bold", 10)
    p.drawString(30, y, "ID")
    p.drawString(60, y, "Concepto")
    p.drawString(160, y, "Fecha")
    p.drawString(230, y, "Metodo")
    p.drawString(300, y, "Valor")

    y -= 20
    p.setFont("Helvetica", 9)

    for pago in pagos:
        p.drawString(30, y, str(pago.id))
        p.drawString(60, y, pago.concepto_pago[:15])  # cortar texto largo
        p.drawString(160, y, str(pago.fecha_pago))
        p.drawString(230, y, pago.metodo_pago)
        p.drawString(300, y, str(pago.valor_total))

        y -= 15

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    return response
