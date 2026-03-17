from django.shortcuts import render, redirect
from .models import Usuario
from django.contrib.auth import authenticate, login as auth_login, logout
from .forms import UsuarioForm

# Create your views here.


def login_view(request):
    if request.method == 'POST':
        username = request.POST['documento']
        password = request.POST['contrasena']
        user = authenticate(request, username=username, password = password)

def usuario(request):
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/list.html", {'usuarios' : usuarios}) #Como decir Index.html del modulo de Usuarios.

def crear_usuario(request):
    formulario = UsuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('usuario')
    return render(request, "usuarios/crear.html" , {'formulario' : formulario})

def consulta_especifica_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    return render(request, "usuarios/especifica.html", {'usuario' : usuario})

def editar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    formulario = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)  #Se instacia del Modelo.
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('usuario')
    return render(request, "usuarios/editar.html", {'formulario' : formulario})

def eliminar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.delete()
    return redirect('usuario')
