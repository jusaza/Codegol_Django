from django import forms
from django.core.exceptions import ValidationError

from .models import ConceptoPago, Pago
from .validators import validar_matricula_vigente, validar_pago_duplicado


class PagoForm(forms.ModelForm):
    nombre_otro = forms.CharField(
        required=False,
        max_length=100,
        label='Nombre del concepto',
    )
    valor_otro = forms.FloatField(
        required=False,
        min_value=0,
        label='Valor',
    )

    class Meta:
        model = Pago
        fields = [
            'id_concepto',
            'fecha_pago',
            'metodo_pago',
            'observaciones',
            'id_matricula',
        ]

    def __init__(self, *args, matriculas_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        widget_class = {'class': 'form-control'}

        self.fields['id_concepto'].queryset = ConceptoPago.objects.filter(activo=True)
        self.fields['id_concepto'].empty_label = 'Seleccione un concepto'
        self.fields['id_concepto'].widget.attrs.update(widget_class)

        self.fields['fecha_pago'].widget = forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                **widget_class,
                'type': 'date',
            },
        )
        self.fields['fecha_pago'].input_formats = ['%Y-%m-%d']
        self.fields['metodo_pago'].widget.attrs.update(widget_class)
        self.fields['observaciones'].widget.attrs.update(widget_class)
        self.fields['nombre_otro'].widget.attrs.update(widget_class)
        self.fields['valor_otro'].widget.attrs.update({**widget_class, 'step': '0.01'})

        if matriculas_queryset is not None:
            self.fields['id_matricula'].queryset = (
                matriculas_queryset.select_related('id_jugador')
            )

        self.fields['id_matricula'].empty_label = 'Seleccione una matrícula'
        self.fields['id_matricula'].widget.attrs.update(widget_class)

        self.fields['id_matricula'].label_from_instance = (
            lambda obj: (
                f"Matrícula #{obj.id} - "
                f"{obj.id_jugador.nombre_completo} - "
                f"CC: {obj.id_jugador.num_identificacion}"
            )
        )
        
        if self.instance.pk:
            self.fields['id_matricula'].disabled = True
            self.fields['id_concepto'].disabled = True
            self.fields['fecha_pago'].disabled = True

        if self.instance.pk and self.instance.id_concepto_id:
            concepto = self.instance.id_concepto
            if concepto.es_otro:
                self.fields['nombre_otro'].initial = self.instance.concepto_pago
                self.fields['valor_otro'].initial = self.instance.valor_total

    def clean(self):
        cleaned = super().clean()
        concepto = cleaned.get('id_concepto')
        matricula = cleaned.get('id_matricula')
        fecha_pago = cleaned.get('fecha_pago')
        nombre_otro = (cleaned.get('nombre_otro') or '').strip()
        valor_otro = cleaned.get('valor_otro')

        if matricula is not None:
            validar_matricula_vigente(matricula)

        if concepto is None or fecha_pago is None or matricula is None:
            return cleaned

        if concepto.es_otro:
            if not nombre_otro:
                self.add_error(
                    'nombre_otro',
                    'Debe indicar el nombre del concepto cuando selecciona "Otro".',
                )
            if valor_otro is None:
                self.add_error(
                    'valor_otro',
                    'Debe indicar el valor cuando selecciona "Otro".',
                )
            elif valor_otro < 0:
                self.add_error('valor_otro', 'El valor no puede ser negativo.')
        else:
            if concepto.valor < 0:
                raise ValidationError(
                    f'El concepto "{concepto.nombre}" no tiene un valor configurado válido.'
                )

        try:
            validar_pago_duplicado(
                concepto,
                matricula,
                fecha_pago,
                pago_excluir=self.instance if self.instance.pk else None,
            )
        except ValidationError as exc:
            raise ValidationError(exc.messages) from exc

        return cleaned

    def save(self, commit=True):
        pago = super().save(commit=False)

        if self.instance.pk:
            # Mantener la matrícula, el concepto y la fecha originales
            pago.id_matricula = self.instance.id_matricula
            pago.id_concepto = self.instance.id_concepto
            pago.fecha_pago = self.instance.fecha_pago

        concepto = pago.id_concepto

        if concepto.es_otro:
            pago.concepto_pago = self.cleaned_data['nombre_otro'].strip()
            pago.valor_total = self.cleaned_data['valor_otro']
        else:
            pago.concepto_pago = concepto.nombre
            if not self.instance.pk:
                pago.valor_total = concepto.valor

        if commit:
            pago.save()

        return pago


class ConceptoPagoValorForm(forms.Form):
    def __init__(self, *args, conceptos=None, **kwargs):
        super().__init__(*args, **kwargs)

        for concepto in conceptos or []:
            self.fields[f'valor_{concepto.id}'] = forms.FloatField(
                min_value=0,
                initial=concepto.valor,
                label=concepto.nombre,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'step': '0.01',
                }),
            )

    def save(self, conceptos):
        for concepto in conceptos:
            field_name = f'valor_{concepto.id}'
            if field_name in self.cleaned_data:
                concepto.valor = self.cleaned_data[field_name]
                concepto.save(update_fields=['valor'])
