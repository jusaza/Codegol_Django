from django import forms
from datetime import date
from .models import Usuario, Rol, Documentos


class UsuarioForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Usuario
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date'}
            )
        }
        exclude = [
            'contrasena',
            'estado',
            'id_usuario_registro',
            'lugar_nacimiento'  # Se usa desde la API.
        ]

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha_nacimiento")
        roles = cleaned_data.get("roles")

        if not fecha:
            return cleaned_data

        hoy = date.today()

        # No permitir fechas futuras
        if fecha > hoy:
            self.add_error(
                "fecha_nacimiento",
                "La fecha de nacimiento no puede ser una fecha futura."
            )
            return cleaned_data

        # Calcular edad
        edad = hoy.year - fecha.year - (
            (hoy.month, hoy.day) < (fecha.month, fecha.day)
        )

        # No permitir edades mayores a 100 años
        if edad > 100:
            self.add_error(
                "fecha_nacimiento",
                "La fecha de nacimiento no es válida."
            )

        if not roles:
            return cleaned_data

        for rol in roles:
            nombre = rol.rol_usuario

            if nombre == "Jugador" and edad < 5:
                self.add_error(
                    "fecha_nacimiento",
                    "Los jugadores deben tener mínimo 5 años."
                )

            elif nombre == "Administrador" and edad < 18:
                self.add_error(
                    "fecha_nacimiento",
                    "El administrador debe ser mayor de edad (18+)."
                )

            elif nombre == "Entrenador" and edad < 18:
                self.add_error(
                    "fecha_nacimiento",
                    "El entrenador debe ser mayor de edad (18+)."
                )

        return cleaned_data


class LoginForm(forms.Form):
    documento = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Documento'})
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )


DOCUMENTOS_POR_ROL = {
    "Administrador": [
        'DNI', 'HOJA_VIDA', 'CERT_ANTECEDENTES', 'CERT_ESTUDIOS',
        'EPS', 'ARL', 'CONTRATO', 'FOTO',
    ],
    "Entrenador": [
        'DNI', 'HOJA_VIDA', 'CERT_ANTECEDENTES', 'CERT_ESTUDIOS',
        'LICENCIA_ENTRENADOR', 'CERT_MEDICO', 'EPS', 'ARL',
        'CONTRATO', 'FOTO',
    ],
    "Jugador": [
        'DNI', 'CERT_MEDICO', 'EPS', 'SEGURO', 'FOTO',
        'CONTRATO', 'COMPROMISO',
    ],
    "JugadorMenor": [
        'REGISTRO_CIVIL', 'AUTORIZACION_PADRES', 'CERT_MEDICO',
        'EPS', 'SEGURO', 'FOTO', 'COMPROMISO',
    ],
}

def es_menor(usuario):
    hoy = date.today()
    edad = hoy.year - usuario.fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (usuario.fecha_nacimiento.month, usuario.fecha_nacimiento.day)
    )
    return edad < 18

class DocumentoForm(forms.ModelForm):

    class Meta:
        model = Documentos
        fields = ['categoria', 'tipo_documento', 'archivo', 'nombre', 'observaciones']

        widgets = {
            'categoria': forms.Select(attrs={'id': 'id_categoria'}),
            'tipo_documento': forms.Select(attrs={'id': 'id_tipo_documento'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'observaciones': forms.TextInput(),
            'archivo': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.categoria_url = kwargs.pop('categoria', None)
        self.categorias_permitidas = kwargs.pop('categorias_permitidas', None)
        super().__init__(*args, **kwargs)
        categorias = list(Documentos.CATEGORIA_CHOICES)
        if self.categorias_permitidas:
            categorias = [
                (k, v) for k, v in Documentos.CATEGORIA_CHOICES
                if k in self.categorias_permitidas
            ]
        self.fields['categoria'].choices = [
            ('', 'Seleccione una categoría')
        ] + categorias
        tipos_permitidos = set()
        if self.usuario:
            roles = self.usuario.roles.values_list('rol_usuario', flat=True)
            for rol in roles:
                if rol == "Jugador" and es_menor(self.usuario):
                    tipos_permitidos.update(DOCUMENTOS_POR_ROL["JugadorMenor"])
                else:
                    tipos_permitidos.update(DOCUMENTOS_POR_ROL.get(rol, []))
        documentos_subidos = set(
            Documentos.objects.filter(usuario=self.usuario)
            .values_list('tipo_documento', flat=True)
        ) if self.usuario else set()
        if self.categoria_url:
            self.fields['categoria'].required = False
            self.fields['categoria'].widget = forms.HiddenInput()
            self.initial['categoria'] = self.categoria_url
            tipos_filtrados = [
                (key, value)
                for key, value in Documentos.DOCUMENTACION
                if key in tipos_permitidos
                and key not in documentos_subidos
                and Documentos.DOCUMENTOS_CATEGORIA_MAP.get(key) == self.categoria_url
            ]
            self.fields['tipo_documento'].choices = (
                [('', 'Seleccione un tipo de documento')] + tipos_filtrados
                if tipos_filtrados else [('', 'Ya todos están subidos')]
            )
        else:
            tipos_disponibles = [
                (key, value)
                for key, value in Documentos.DOCUMENTACION
                if key in tipos_permitidos and key not in documentos_subidos
            ]

            self.fields['tipo_documento'].choices = (
                [('', 'Seleccione un tipo de documento')] + tipos_disponibles
                if tipos_disponibles else [('', 'Ya todos están subidos')]
            )

        self.fields['categoria'].required = True
        self.fields['tipo_documento'].required = True
        self.fields['archivo'].required = True
        self.fields['nombre'].required = True
        self.fields['observaciones'].required = False
    def clean(self):
        cleaned_data = super().clean()
        if self.categoria_url:
            cleaned_data['categoria'] = self.categoria_url
        tipo_documento = cleaned_data.get('tipo_documento')
        if self.usuario and tipo_documento:
            existente = Documentos.objects.filter(
                usuario=self.usuario,
                tipo_documento=tipo_documento
            ).first()
            if existente:
                if existente.estado == "APROBADO":
                    raise forms.ValidationError("Este documento ya fue aprobado")
                if existente.estado == "PENDIENTE":
                    raise forms.ValidationError("Este documento ya está en revisión")
                if existente.estado == "DEVUELTO":
                    self.instance.id = existente.id
        return cleaned_data
    
class EditarPerfil(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            "correo",
            "contrasena",
            "num_identificacion",
            "tipo_documento",
            "telefono_1",
            "telefono_2",
            "direccion",
            "foto_perfil"
        ]
