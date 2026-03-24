from django import forms
from .models import Usuario,Rol,Documentos

class UsuarioForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.all(),
        widget=forms.CheckboxSelectMultiple()
        )
    class Meta:
        model = Usuario
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }
        exclude = ['estado', 'id_usuario_registro']

class LoginForm(forms.Form):
        documento = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Documento'}))
        contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documentos
        fields = ['archivo', 'nombre']
