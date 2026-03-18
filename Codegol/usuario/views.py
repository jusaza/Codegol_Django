from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, DetallesUsuarioRol
from .forms import UsuarioForm, LoginForm
from .decorators import rol_requerido

# Create your views here.

def login_view(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            documento = form.cleaned_data["documento"]
            contrasena = form.cleaned_data["contrasena"]

            try:
                usuario = Usuario.objects.get(
                    num_identificacion = documento,
                    contrasena = contrasena
                )

                roles = DetallesUsuarioRol.objects.filter(
                    id_usuario=usuario).select_related("id_rol")

                lista_roles = [r.id_rol.rol_usuario for r in roles]

                request.session["usuario_id"] = usuario.id_usuario    #Nombres personalizados para guardar la sesion ejemplo [usuario_id] y despues va el campo de la base de datos.
                request.session["nombre"] = usuario.nombre_completo
                request.session["roles"] = lista_roles

                return redirect("pagina_original")
            
            except Usuario.DoesNotExist:
                messages.error(request, "Documento o contraseña incorrectos")
                return redirect("login")
            
    return render(request, "login.html", {"form" : form})

def logout_view(request):
    request.session.flush()
    return redirect("login")

@rol_requerido(["Entrenador"])
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
