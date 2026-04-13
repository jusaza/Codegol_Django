import csv

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

def cargar_usuarios_csv(request):
    if request.method == "POST":
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, "Debes seleccionar un archivo CSV.")
            return redirect('carga_masiva_usuario')
        decoded_file = archivo.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        columnas_requeridas = [
            'correo',
            'contrasena',
            'nombre_completo',
            'num_identificacion',
            'tipo_documento',
            'telefono_1',
            'direccion',
            'genero',
            'fecha_nacimiento',
            'grupo_sanguineo',
            'rol'
        ]
        columnas_faltantes = [col for col in columnas_requeridas if col not in reader.fieldnames]
        if columnas_faltantes:
            messages.error(
                request,
                f"❌ Faltan columnas en el CSV: {', '.join(columnas_faltantes)}"
            )
            return redirect('carga_masiva_usuario')
        usuario_sesion_id = request.session.get("usuario_id")
        if not usuario_sesion_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect('login')
        usuarios_creados = []
        duplicados = 0
        for row in reader:
            correo = row['correo']
            documento = row['num_identificacion']
            rol_nombre = row.get('rol')
            if Usuario.objects.filter(correo=correo).exists():
                duplicados += 1
                continue
            if Usuario.objects.filter(num_identificacion=documento).exists():
                duplicados += 1
                continue
            usuario = Usuario(
                correo=correo,
                contrasena=row['contrasena'],
                nombre_completo=row['nombre_completo'],
                num_identificacion=documento,
                tipo_documento=row['tipo_documento'],
                telefono_1=row['telefono_1'],
                direccion=row['direccion'],
                genero=row['genero'],
                fecha_nacimiento=row['fecha_nacimiento'],
                grupo_sanguineo=row['grupo_sanguineo'],
                estado=True,
                id_usuario_registro_id=usuario_sesion_id
            )
            usuarios_creados.append((usuario, rol_nombre))
        Usuario.objects.bulk_create([u[0] for u in usuarios_creados])
        for usuario, rol_nombre in usuarios_creados:
            try:
                rol = Rol.objects.get(rol_usuario=rol_nombre)
                usuario_guardado = Usuario.objects.get(correo=usuario.correo)

                if not DetallesUsuarioRol.objects.filter(
                    id_usuario=usuario_guardado,
                    id_rol=rol
                ).exists():
                    DetallesUsuarioRol.objects.create(
                        id_usuario=usuario_guardado,
                        id_rol=rol
                    )

            except Rol.DoesNotExist:
                continue
        if usuarios_creados:
            messages.success(
                request,
                f"✅ Usuarios creados: {len(usuarios_creados)}"
            )
        if duplicados > 0:
            messages.error(
                request,
                f"❌ Duplicados omitidos: {duplicados}"
            )
        return redirect('carga_masiva_usuario')
    return render(request, 'usuarios/cargar.html')

@rol_requerido(["Administrador"])
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

@rol_requerido(["Administrador", "Entrenador", "Jugador"])
def documentos(request,id):
    usuario = Usuario.objects.get(id_usuario=id)
    documentos = Documentos.objects.filter(usuario=usuario)
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
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

@rol_requerido(["Administrador"])
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
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
    return render(request, "usuarios/especifica.html", {'usuario' : usuario, 'roles_usuario' : roles_usuario})

def editar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    formulario = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)  #Se instacia del Modelo.
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
    if formulario.is_valid() and request.POST:
        usuario = formulario.save(commit=False)
        formulario.save()
        formulario.save_m2m()
        return redirect('usuario')
    return render(request, "usuarios/usuario_form.html", {'formulario' : formulario})

def editar_perfil(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    formulario = EditarPerfil(request.POST or None, request.FILES or None, instance=usuario)  #Se instacia del Modelo.
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
    if formulario.is_valid() and request.POST:
        usuario = formulario.save(commit=False)
        formulario.save()
        return redirect('mi_perfil', id=usuario.id_usuario)
    return render(request, "usuarios/editar_perfil.html", {'formulario' : formulario})

@rol_requerido(["Administrador"])
def reactivar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.estado = True
    usuario.save()
    return redirect('usuario')

@rol_requerido(["Administrador"])
def eliminar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.estado = False
    usuario.save()
    return redirect('usuario')

@rol_requerido(["Administrador"])
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
