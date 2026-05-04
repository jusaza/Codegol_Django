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
        widgets = {'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})}
        exclude = ['estado', 'id_usuario_registro', 'lugar_nacimiento'] # campo de lugar_nacimiento se usa desde la API.
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha_nacimiento")
        roles = cleaned_data.get("roles")
        if not fecha or not roles:
            return cleaned_data
        hoy = date.today()
        edad = hoy.year - fecha.year - (
            (hoy.month, hoy.day) < (fecha.month, fecha.day))
        for rol in roles:
            nombre = rol.rol_usuario
            if nombre == "Jugador" and edad < 5:
                self.add_error("fecha_nacimiento", "Jugadores requiere mínimo 5 años.")
            if nombre in ["Administrador"] and edad < 18:
                self.add_error("fecha_nacimiento", "Administrador debe ser mayor de edad (18+).")
            if nombre == "Entrenador" and edad < 18:
                self.add_error("fecha_nacimiento", "Entrenador debe ser mayor de edad (18+).")
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
        super().__init__(*args, **kwargs)

        self.fields['categoria'].choices = [
            ('', 'Seleccione una categoría')
        ] + list(Documentos.CATEGORIA_CHOICES)

        tipos_permitidos = set()

        if self.usuario:
            roles = self.usuario.roles.values_list('rol_usuario', flat=True)

            for rol in roles:
                if rol == "Jugador" and es_menor(self.usuario):
                    tipos_permitidos.update(DOCUMENTOS_POR_ROL["JugadorMenor"])
                else:
                    tipos_permitidos.update(DOCUMENTOS_POR_ROL.get(rol, []))

        self.fields['tipo_documento'].choices = [
            ('', 'Seleccione un tipo de documento')
        ] + [
            (key, value)
            for key, value in Documentos.DOCUMENTACION
            if key in tipos_permitidos
        ]

        self.fields['categoria'].required = True
        self.fields['tipo_documento'].required = True
        self.fields['archivo'].required = True
        self.fields['nombre'].required = True
        self.fields['observaciones'].required = False

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        tipo_documento = cleaned_data.get('tipo_documento')

        if categoria and tipo_documento:
            categoria_correcta = Documentos.DOCUMENTOS_CATEGORIA_MAP.get(tipo_documento)

            if categoria_correcta and categoria_correcta != categoria:
                raise forms.ValidationError(
                    "El documento no pertenece a esa categoría."
                )
            
        if self.usuario and tipo_documento:
            if Documentos.objects.filter(usuario=self.usuario, tipo_documento=tipo_documento).exists():
                raise forms.ValidationError("Ya has subido este documento")

        return cleaned_data

class EditarPerfil(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            "correo",
            "contrasena",
            "num_identificacion",
            "telefono_1",
            "telefono_2",
            "direccion",
            "foto_perfil"
        ]
