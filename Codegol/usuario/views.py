from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario, DetallesUsuarioRol, Documentos, Rol
from .forms import UsuarioForm, LoginForm, DocumentoForm, EditarPerfil
from .decorators import rol_requerido
from django.db.models import Q

# Create your views here.

def login(request):
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

                print(lista_roles)

                return redirect("pagina_original")
            
            
            except Usuario.DoesNotExist:
                messages.error(request, "Documento o contraseña incorrectos")
                return redirect("login")
            
    return render(request, "login.html", {"form" : form})

def logout(request):
    request.session.flush()
    return redirect("login")

@rol_requerido(["Administrador", "Entrenador"])
def usuario(request):
    usuarios = Usuario.objects.filter(estado=True)
    busqueda = request.GET.get('busqueda', '')
    rol_id = request.GET.get('rol', '')
    if busqueda:
        usuarios = usuarios.filter(Q(nombre_completo__icontains=busqueda) | Q(correo__icontains=busqueda) | Q(num_identificacion__exact=busqueda if busqueda.isdigit() else None))
    if rol_id:
        # Filtramos usando la tabla intermedia de roles
        usuarios = usuarios.filter(roles__id_rol=rol_id).distinct()
    roles = Rol.objects.filter(estado=True)
    return render(request, "usuarios/list.html", {'usuarios': usuarios,'roles': roles,'busqueda': busqueda,'rol_id': rol_id})

def documentos(request,id):
    usuario = Usuario.objects.get(id_usuario=id)
    documentos = Documentos.objects.filter(usuario=usuario)
    if request.method == 'POST':
        formulario = DocumentoForm(request.POST, request.FILES)
        if formulario.is_valid():
            documento = formulario.save(commit=False)  # se crea pero todavia no se guarda.
            documento.usuario = usuario          # aquí se asigna al usuario.
            documento.save()                     # ahora sí se guarda el archivo.
            return redirect('documentos', id=usuario.id_usuario)
    else:
        formulario = DocumentoForm()
    return render(request, 'usuarios/documentos.html', {'formulario': formulario, 'documentos': documentos, 'usuario': usuario})

def borrar_documento(request, id):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login") 
    documento = get_object_or_404(Documentos, id_archivo=id)
    if documento.usuario.id_usuario == usuario_id:
        if documento.archivo:
            documento.archivo.delete(save=False)
        documento.delete()
    return redirect("documentos", id=usuario_id)

def crear_usuario(request):
    formulario = UsuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        usuario = formulario.save(commit=False)
        formulario.save()
        formulario.save_m2m()
        return redirect('usuario')
    return render(request, "usuarios/usuario_form.html" , {'formulario' : formulario})

def consulta_especifica_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    roles_usuario = list(usuario.roles.values_list('id_rol', flat=True))
    return render(request, "usuarios/especifica.html", {'usuario' : usuario, 'roles_usuario' : roles_usuario})

def editar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    formulario = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)  #Se instacia del Modelo.
    if formulario.is_valid() and request.POST:
        usuario = formulario.save(commit=False)
        formulario.save()
        formulario.save_m2m()
        return redirect('usuario')
    return render(request, "usuarios/usuario_form.html", {'formulario' : formulario})

def reactivar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.estado = True
    usuario.save()
    return redirect('usuario')

def eliminar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.estado = False
    usuario.save()
    return redirect('usuario')

def usuarios_inactivos(request):
    busqueda = request.GET.get('busqueda', '')
    rol_id = request.GET.get('rol', '')
    usuarios = Usuario.objects.filter(estado=False)
    if busqueda:
        usuarios = usuarios.filter(nombre_completo__icontains=busqueda)
    if rol_id:
        usuarios = usuarios.filter(roles__id_rol=rol_id).distinct()
    roles = Rol.objects.all()
    return render(request, 'usuarios/inactivos.html', {
        'usuarios': usuarios,'roles': roles,'busqueda': busqueda,'rol_id': rol_id})
