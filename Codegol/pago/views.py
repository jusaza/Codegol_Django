from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
from django.db.models import Sum, Q
from django.core.paginator import Paginator
import json

from matricula.models import Matricula
from usuario.models import DetallesUsuarioRol, Usuario
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
            Q(pk__in=matriculas.values_list('pk', flat=True)) |
            Q(pk=pago.id_matricula_id),
        ).select_related('id_jugador').order_by('-fecha_matricula')

    if request.method == 'POST':
        form = PagoForm(
            request.POST,
            instance=pago,
            matriculas_queryset=matriculas,
        )

        if form.is_valid():
            form.save()

            # Si el formulario fue enviado desde el modal (AJAX)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "redirect_url": reverse("lista_pagos"),
                })

            return redirect("lista_pagos")

        # Si hay errores y viene desde el modal
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(
                request,
                "pago/formulario.html",
                _contexto_formulario_pago(form, matriculas) | {"pago": pago},
            )

        # Si no es AJAX
        return render(
            request,
            "pago/formulario.html",
            _contexto_formulario_pago(form, matriculas) | {"pago": pago},
        )

    form = PagoForm(
        instance=pago,
        matriculas_queryset=matriculas,
    )

    return render(
        request,
        "pago/formulario.html",
        _contexto_formulario_pago(form, matriculas) | {"pago": pago},
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

    total = Pago.objects.aggregate(
        Sum('valor_total'),
    )['valor_total__sum'] or 0
    p.drawString(50, 760, f'Total recaudado: ${total}')

    pagos = Pago.objects.all()

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


def _formatear_moneda(valor):
    return f"${valor:,.0f}".replace(",", ".")


def _calcular_estado_cuenta(jugador):
    # Obtener matrículas activas del jugador
    matriculas = Matricula.objects.filter(
        id_jugador=jugador,
        estado=True
    ).order_by('-fecha_inicio')

    # Obtener valores configurados
    concepto_m = ConceptoPago.objects.filter(
        nombre=ConceptoPago.NOMBRE_MATRICULA
    ).first()

    concepto_mens = ConceptoPago.objects.filter(
        nombre=ConceptoPago.NOMBRE_MENSUALIDAD
    ).first()

    concepto_u = ConceptoPago.objects.filter(
        nombre=ConceptoPago.NOMBRE_UNIFORME
    ).first()

    val_m = concepto_m.valor if concepto_m else 0.0
    val_mens = concepto_mens.valor if concepto_mens else 0.0
    val_u = concepto_u.valor if concepto_u else 0.0

    total_facturado_matricula = 0.0
    total_facturado_mensualidad = 0.0
    total_facturado_uniforme = 0.0
    total_facturado_otro = 0.0

    detalles_matriculas = []

    MESES = [
        "",
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    def sumar_meses(fecha, cantidad):
        mes = fecha.month + cantidad
        while mes > 12:
            mes -= 12
        return MESES[mes]

    for m in matriculas:
        inicio = m.fecha_inicio
        fin = m.fecha_fin

        num_meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month) + 1

        if num_meses < 1:
            num_meses = 1

        fact_m = val_m
        fact_mens = num_meses * val_mens
        fact_u = val_u

        total_facturado_matricula += fact_m
        total_facturado_mensualidad += fact_mens
        total_facturado_uniforme += fact_u

        detalles_matriculas.append({
            "matricula": m,
            "meses": num_meses,
            "facturado_matricula": fact_m,
            "facturado_mensualidad": fact_mens,
            "facturado_uniforme": fact_u,
            "total": fact_m + fact_mens + fact_u
        })

    pagos = Pago.objects.filter(
        id_matricula__in=matriculas,
        cancelado=False
    ).select_related(
        "id_matricula"
    ).order_by("-fecha_pago")

    total_pagado_matricula = 0.0
    total_pagado_mensualidad = 0.0
    total_pagado_uniforme = 0.0
    total_pagado_otro = 0.0

    # Agregar descripción amigable para mostrar en el estado de cuenta
    for p in pagos:

        concepto = p.concepto_pago

        if p.id_matricula:

            # Mes de la matrícula
            mes_matricula = f"{MESES[p.id_matricula.fecha_inicio.month]} {p.id_matricula.fecha_inicio.year}"

            # Mes en el que realmente se realizó el pago
            mes_pago = f"{MESES[p.fecha_pago.month]} {p.fecha_pago.year}"

            if concepto == ConceptoPago.NOMBRE_MATRICULA:
                p.concepto_mostrar = f"Matrícula {mes_matricula}"

            elif concepto == ConceptoPago.NOMBRE_MENSUALIDAD:
                p.concepto_mostrar = f"Mensualidad {mes_pago}"

            elif concepto == ConceptoPago.NOMBRE_UNIFORME:
                p.concepto_mostrar = f"Uniforme {mes_pago}"

            else:
                p.concepto_mostrar = concepto

        else:
            p.concepto_mostrar = concepto

        val = p.valor_total

        if concepto == ConceptoPago.NOMBRE_MATRICULA:
            total_pagado_matricula += val

        elif concepto == ConceptoPago.NOMBRE_MENSUALIDAD:
            total_pagado_mensualidad += val

        elif concepto == ConceptoPago.NOMBRE_UNIFORME:
            total_pagado_uniforme += val

        else:
            total_pagado_otro += val
            total_facturado_otro += val

    resumen = [
        {
            "concepto": "Matrícula",
            "facturado": total_facturado_matricula,
            "pagado": total_pagado_matricula,
            "pendiente": max(0.0, total_facturado_matricula - total_pagado_matricula)
        },
        {
            "concepto": "Mensualidades",
            "facturado": total_facturado_mensualidad,
            "pagado": total_pagado_mensualidad,
            "pendiente": max(0.0, total_facturado_mensualidad - total_pagado_mensualidad)
        },
        {
            "concepto": "Uniformes",
            "facturado": total_facturado_uniforme,
            "pagado": total_pagado_uniforme,
            "pendiente": max(0.0, total_facturado_uniforme - total_pagado_uniforme)
        },
        {
            "concepto": "Otros Conceptos",
            "facturado": total_facturado_otro,
            "pagado": total_pagado_otro,
            "pendiente": max(0.0, total_facturado_otro - total_pagado_otro)
        }
    ]

    grand_total_facturado = (
        total_facturado_matricula +
        total_facturado_mensualidad +
        total_facturado_uniforme +
        total_facturado_otro
    )

    grand_total_pagado = (
        total_pagado_matricula +
        total_pagado_mensualidad +
        total_pagado_uniforme +
        total_pagado_otro
    )

    grand_saldo_pendiente = max(
        0.0,
        grand_total_facturado - grand_total_pagado
    )

    estado_paz_salvo = (
        "Paz y Salvo"
        if grand_saldo_pendiente <= 0
        else "Saldo Pendiente"
    )

    return {
        "matriculas": detalles_matriculas,
        "pagos": pagos,
        "resumen": resumen,
        "total_facturado": grand_total_facturado,
        "total_pagado": grand_total_pagado,
        "saldo_pendiente": grand_saldo_pendiente,
        "estado_paz_salvo": estado_paz_salvo,
    }


def estado_cuenta_jugador(request, usuario_id):
    # Validar permisos
    logged_in_uid = request.session.get('usuario_id')
    roles = request.session.get('roles', [])
    es_admin = 'Administrador' in roles
    
    if not logged_in_uid:
        return redirect('login')
        
    if not es_admin and int(usuario_id) != int(logged_in_uid):
        return HttpResponse("No tiene permisos para acceder a esta información.", status=403)
        
    jugador = get_object_or_404(Usuario, pk=usuario_id)
    
    # Verificar que el usuario tenga rol de Jugador (o si es admin, permitir ver igual)
    es_jugador = DetallesUsuarioRol.objects.filter(
        id_usuario=jugador,
        id_rol__rol_usuario__iexact='Jugador'
    ).exists()
    
    if not es_jugador and not es_admin:
        return HttpResponse("El usuario especificado no es un jugador.", status=400)
        
    datos = _calcular_estado_cuenta(jugador)
    
    # Formatear datos para la plantilla HTML
    resumen_fmt = []
    for item in datos['resumen']:
        resumen_fmt.append({
            'concepto': item['concepto'],
            'facturado': _formatear_moneda(item['facturado']),
            'pagado': _formatear_moneda(item['pagado']),
            'pendiente': _formatear_moneda(item['pendiente']),
        })
        
    matriculas_fmt = []
    for dm in datos['matriculas']:
        matriculas_fmt.append({
            'id': dm['matricula'].id,
            'fecha_inicio': dm['matricula'].fecha_inicio,
            'fecha_fin': dm['matricula'].fecha_fin,
            'nivel': dm['matricula'].nivel,
            'meses': dm['meses'],
            'facturado_matricula': _formatear_moneda(dm['facturado_matricula']),
            'facturado_mensualidad': _formatear_moneda(dm['facturado_mensualidad']),
            'facturado_uniforme': _formatear_moneda(dm['facturado_uniforme']),
            'total': _formatear_moneda(dm['total']),
        })
        
    pagos_fmt = []
    for p in datos['pagos']:
        pagos_fmt.append({
            'id': p.id,
            'concepto_pago': p.concepto_mostrar,
            'fecha_pago': p.fecha_pago,
            'metodo_pago': p.metodo_pago,
            'observaciones': p.observaciones or 'N/A',
            'valor_total': _formatear_moneda(p.valor_total),
        })
        
    contexto = {
        'jugador': jugador,
        'matriculas': matriculas_fmt,
        'pagos': pagos_fmt,
        'resumen': resumen_fmt,
        'total_facturado': _formatear_moneda(datos['total_facturado']),
        'total_pagado': _formatear_moneda(datos['total_pagado']),
        'saldo_pendiente': _formatear_moneda(datos['saldo_pendiente']),
        'estado_paz_salvo': datos['estado_paz_salvo'],
        'fecha_hoy': datetime.now().strftime("%Y-%m-%d"),
    }
    
    return render(request, 'pago/estado_cuenta.html', contexto)


def estado_cuenta_pdf(request, usuario_id):
    # Validar permisos
    logged_in_uid = request.session.get('usuario_id')
    roles = request.session.get('roles', [])
    es_admin = 'Administrador' in roles
    
    if not logged_in_uid:
        return redirect('login')
        
    if not es_admin and int(usuario_id) != int(logged_in_uid):
        return HttpResponse("No tiene permisos para acceder a esta información.", status=403)
        
    jugador = get_object_or_404(Usuario, pk=usuario_id)
    
    # Calcular estado de cuenta
    datos = _calcular_estado_cuenta(jugador)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="estado_cuenta_{jugador.num_identificacion}.pdf"'
    
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#001f3f'),
        spaceAfter=5,
        alignment=1
    )
    
    style_subtitle = ParagraphStyle(
        name='SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#001f3f'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    style_normal = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        leading=12
    )
    
    story = []
    
    story.append(Paragraph("ESCUELA DE FÚTBOL CODEGOL", style_title))
    story.append(Paragraph("REPORTE - ESTADO DE CUENTA JUGADOR", ParagraphStyle('Sub', parent=style_title, fontSize=12, spaceAfter=20)))
    story.append(Spacer(1, 10))
    
    # Tabla información jugador
    status_text = datos['estado_paz_salvo'].upper()
    status_color = '#28a745' if datos['saldo_pendiente'] <= 0 else '#dc3545'
    
    info_data = [
        [Paragraph("<b>Nombre Completo:</b>", style_normal), Paragraph(jugador.nombre_completo, style_normal),
         Paragraph("<b>Identificación:</b>", style_normal), Paragraph(f"{jugador.get_tipo_documento_display() or jugador.tipo_documento.upper()} {jugador.num_identificacion}", style_normal)],
        [Paragraph("<b>Correo Electrónico:</b>", style_normal), Paragraph(jugador.correo, style_normal),
         Paragraph("<b>Teléfono:</b>", style_normal), Paragraph(jugador.telefono_1, style_normal)],
        [Paragraph("<b>Fecha de Emisión:</b>", style_normal), Paragraph(datetime.now().strftime("%Y-%m-%d %I:%M %p"), style_normal),
         Paragraph("<b>Estado Financiero:</b>", style_normal), Paragraph(f"<font color='{status_color}'><b>{status_text}</b></font>", style_normal)]
    ]
    
    info_table = Table(info_data, colWidths=[110, 160, 110, 160])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Resumen de Saldos
    story.append(Paragraph("Resumen de Saldos", style_subtitle))
    
    summary_headers = ["Concepto", "Facturado (Billed)", "Pagado (Paid)", "Saldo Pendiente (Balance)"]
    summary_rows = []
    
    for item in datos['resumen']:
        summary_rows.append([
            item['concepto'],
            _formatear_moneda(item['facturado']),
            _formatear_moneda(item['pagado']),
            _formatear_moneda(item['pendiente'])
        ])
        
    summary_rows.append([
        "TOTAL",
        _formatear_moneda(datos['total_facturado']),
        _formatear_moneda(datos['total_pagado']),
        _formatear_moneda(datos['saldo_pendiente'])
    ])
    
    summary_table = Table([summary_headers] + summary_rows, colWidths=[150, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001f3f')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.black),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # Historial de Matrículas
    if datos['matriculas']:
        story.append(Paragraph("Detalle de Matrículas Vigentes e Historial", style_subtitle))
        mat_headers = ["ID", "Fecha Inicio", "Fecha Fin", "Nivel", "Meses", "Billed Total"]
        mat_rows = []
        for dm in datos['matriculas']:
            mat_rows.append([
                str(dm['matricula'].id),
                str(dm['matricula'].fecha_inicio),
                str(dm['matricula'].fecha_fin),
                dm['matricula'].nivel,
                str(dm['meses']),
                _formatear_moneda(dm['total'])
            ])
        mat_table = Table([mat_headers] + mat_rows, colWidths=[40, 100, 100, 90, 70, 140])
        mat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0a192f')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(mat_table)
        story.append(Spacer(1, 15))
        
    # Historial de Pagos
    story.append(Paragraph("Historial de Pagos Recibidos", style_subtitle))
    if datos['pagos'].exists():
        pago_headers = ["ID", "Concepto", "Fecha Pago", "Método", "Valor Pagado"]
        pago_rows = []
        for p in datos['pagos']:
            pago_rows.append([
                str(p.id),
                p.concepto_pago,
                str(p.fecha_pago),
                p.metodo_pago,
                _formatear_moneda(p.valor_total)
            ])
        pago_table = Table([pago_headers] + pago_rows, colWidths=[50, 150, 110, 110, 120])
        pago_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(pago_table)
    else:
        story.append(Paragraph("No se registran pagos aprobados para este jugador.", style_normal))
        
    story.append(Spacer(1, 40))
    
    # Firmas
    sig_data = [
        [Paragraph("___________________________________", style_normal), Paragraph("___________________________________", style_normal)],
        [Paragraph("<b>Firma del Administrador / Cajero</b>", style_normal), Paragraph("<b>Firma del Padre de Familia / Jugador</b>", style_normal)],
        [Paragraph("Escuela de Fútbol Codegol", style_normal), Paragraph("Aceptación de Saldo y Compromiso", style_normal)]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    
    story.append(KeepTogether(sig_table))
    
    doc.build(story)
    return response
