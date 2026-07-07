from datetime import date

from django.core.exceptions import ValidationError

from matricula.models import Matricula

from .models import ConceptoPago, Pago


def obtener_matriculas_vigentes():
    hoy = date.today()
    return Matricula.objects.filter(
        estado=True,
        id_jugador__estado=True,
        fecha_fin__gte=hoy,
    ).select_related('id_jugador').order_by('-fecha_matricula')


def validar_matricula_vigente(matricula, fecha_pago):
    if matricula is None:
        raise ValidationError('Debe seleccionar una matrícula.')

    if not matricula.estado:
        raise ValidationError('La matrícula seleccionada no está activa.')

    if not matricula.id_jugador.estado:
        raise ValidationError(
            'El jugador asociado a la matrícula no está activo.'
        )

    if fecha_pago < matricula.fecha_inicio:
        raise ValidationError(
            'La fecha del pago no puede ser anterior al inicio de la matrícula.'
        )

    if fecha_pago > matricula.fecha_fin:
        raise ValidationError(
            'La fecha del pago no puede ser posterior al fin de la matrícula.'
        )


def validar_pago_duplicado(concepto, matricula, fecha_pago, pago_excluir=None, concepto_pago_desc=None):
    pagos = Pago.objects.filter(
        id_matricula=matricula,
    )

    if pago_excluir is not None:
        pagos = pagos.exclude(pk=pago_excluir.pk)

    if concepto.nombre == ConceptoPago.NOMBRE_MATRICULA:
        if pagos.filter(id_concepto__nombre=ConceptoPago.NOMBRE_MATRICULA).exists():
            raise ValidationError(
                'Ya existe un pago de matrícula registrado para esta matrícula '
                'en el período vigente.'
            )

    elif concepto.nombre == ConceptoPago.NOMBRE_MENSUALIDAD:
        if concepto_pago_desc:
            if pagos.filter(concepto_pago__iexact=concepto_pago_desc).exists():
                raise ValidationError(
                    f'Ya existe una mensualidad registrada para el mes seleccionado ({concepto_pago_desc.replace("Mensualidad - ", "")}) en esta matrícula.'
                )
        else:
            if pagos.filter(
                id_concepto__nombre=ConceptoPago.NOMBRE_MENSUALIDAD,
                fecha_pago__year=fecha_pago.year,
                fecha_pago__month=fecha_pago.month,
            ).exists():
                raise ValidationError(
                    f'Ya existe una mensualidad registrada para '
                    f'{fecha_pago.strftime("%B %Y")} en esta matrícula.'
                )
            

    
