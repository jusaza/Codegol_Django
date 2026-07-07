from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
from django.db.models import Sum, Q
from django.core.paginator import Paginator
import json

from matricula.models import Matricula
from usuario.models import DetallesUsuarioRol
from .models import ConceptoPago, Pago
from .forms import PagoForm, ConceptoPagoValorForm
from .validators import obtener_matriculas_vigentes


def _es_administrador(request):
    return 'Administrador' in request.session.get('roles', [])


def _contexto_formulario_pago(form, matriculas):
    conceptos = ConceptoPago.objects.filter(activo=True)
    concepto_otro = ConceptoPago.objects.filter(
        nombre=ConceptoPago.NOMBRE_OTRO,
    ).first()

    return {
        'form': form,
        'matriculas': matriculas,
        'conceptos_json': json.dumps([
            {
                'id': c.id,
                'nombre': c.nombre,
                'valor': c.valor,
                'es_otro': c.es_otro,
            }
            for c in conceptos
        ]),
        'concepto_otro_id': concepto_otro.id if concepto_otro else None,
        'sin_matriculas_vigentes': not matriculas.exists(),
    }


def lista_pagos(request):
    query = request.GET.get('q')
    usuario_id = request.session.get('usuario_id')

    es_jugador = DetallesUsuarioRol.objects.filter(
        id_usuario_id=usuario_id,
        id_rol__rol_usuario__iexact='Jugador',
    ).exists()

    if es_jugador:
        pagos = Pago.objects.filter(
            id_matricula__id_jugador__id_usuario=usuario_id,
        ).select_related('id_matricula__id_jugador', 'id_concepto')
    else:
        pagos = Pago.objects.all().select_related(
            'id_matricula__id_jugador',
            'id_concepto',
        )

    if query:
        pagos = pagos.filter(concepto_pago__icontains=query)

    paginator = Paginator(pagos.order_by('-id'), 10)
    page_number = request.GET.get('page')
    pagos = paginator.get_page(page_number)

    contexto = {
        'pagos': pagos,
        'query': query,
    }

    if _es_administrador(request):
        conceptos = ConceptoPago.objects.filter(activo=True).exclude(
            nombre=ConceptoPago.NOMBRE_OTRO,
        )
        contexto['conceptos_config'] = conceptos
        contexto['form_conceptos'] = ConceptoPagoValorForm(conceptos=conceptos)

    return render(request, 'pago/lista.html', contexto)


def actualizar_valores_conceptos(request):
    if not _es_administrador(request):
        return redirect('lista_pagos')

    conceptos = ConceptoPago.objects.filter(activo=True).exclude(
        nombre=ConceptoPago.NOMBRE_OTRO,
    )

    if request.method == 'POST':
        form = ConceptoPagoValorForm(request.POST, conceptos=conceptos)
        if form.is_valid():
            form.save(conceptos)
            messages.success(request, 'Valores de conceptos actualizados correctamente.')
        else:
            messages.error(request, 'No se pudieron actualizar los valores. Revise los datos.')
        return redirect('lista_pagos')

    return redirect('lista_pagos')


from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse


def crear_pago(request):
    matriculas = obtener_matriculas_vigentes()

    if request.method == 'POST':
        form = PagoForm(
            request.POST,
            matriculas_queryset=matriculas,
        )

        if form.is_valid():
            form.save()

            # Si el formulario fue enviado desde el modal mediante fetch()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('lista_pagos'),
                })

            return redirect('lista_pagos')

        # Si hay errores y viene del modal, devolver nuevamente el formulario
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(
                request,
                'pago/formulario.html',
                _contexto_formulario_pago(form, matriculas),
            )

        # Si no es AJAX, mostrar el formulario normalmente
        return render(
            request,
            'pago/formulario.html',
            _contexto_formulario_pago(form, matriculas),
        )

    form = PagoForm(
        matriculas_queryset=matriculas,
    )

    return render(
        request,
        'pago/formulario.html',
        _contexto_formulario_pago(form, matriculas),
    )


def editar_pago(request, id):
    pago = get_object_or_404(Pago, pk=id)
    matriculas = obtener_matriculas_vigentes()

    if pago.id_matricula_id and not matriculas.filter(pk=pago.id_matricula_id).exists():
        matriculas = Matricula.objects.filter(
            Q(pk__in=matriculas.values_list('pk', flat=True)) | Q(pk=pago.id_matricula_id),
        ).select_related('id_jugador').order_by('-fecha_matricula')

    if request.method == 'POST':
        form = PagoForm(
            request.POST,
            instance=pago,
            matriculas_queryset=matriculas,
        )
        if form.is_valid():
            form.save()
            return redirect('lista_pagos')

        return render(
            request,
            'pago/formulario.html',
            _contexto_formulario_pago(form, matriculas) | {'pago': pago},
        )

    form = PagoForm(instance=pago, matriculas_queryset=matriculas)
    return render(
        request,
        'pago/formulario.html',
        _contexto_formulario_pago(form, matriculas) | {'pago': pago},
    )


def cancelar_pago(request, id):
    pago = Pago.objects.get(id=id)
    pago.cancelado = not pago.cancelado
    pago.save()
    return redirect('lista_pagos')


def reporte_pagos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_pagos.pdf"'

    p = canvas.Canvas(response)

    p.setFont('Helvetica-Bold', 14)
    p.drawString(180, 800, 'Reporte General de Pagos')

    p.setFont('Helvetica', 10)
    p.drawString(50, 780, f'Fecha: {datetime.now().strftime("%Y-%m-%d")}')

    total = Pago.objects.filter(cancelado=False).aggregate(
        Sum('valor_total'),
    )['valor_total__sum'] or 0
    p.drawString(50, 760, f'Total recaudado: ${total}')

    pagos = Pago.objects.filter(cancelado=False)

    y = 730

    p.setFont('Helvetica-Bold', 10)
    p.drawString(30, y, 'ID')
    p.drawString(60, y, 'Concepto')
    p.drawString(160, y, 'Fecha')
    p.drawString(230, y, 'Metodo')
    p.drawString(300, y, 'Valor')

    y -= 20
    p.setFont('Helvetica', 9)

    for pago in pagos:
        p.drawString(30, y, str(pago.id))
        p.drawString(60, y, pago.concepto_pago[:15])
        p.drawString(160, y, str(pago.fecha_pago))
        p.drawString(230, y, pago.metodo_pago)
        p.drawString(300, y, str(pago.valor_total))

        y -= 15

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    return response
