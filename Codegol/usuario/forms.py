from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        exclude = ['estado', 'id_usuario_registro']

class LoginForm(forms.Form):
        documento = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Documento'}))
        contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
