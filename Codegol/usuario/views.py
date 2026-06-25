import csv
import requests
import json

from datetime import date
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario, DetallesUsuarioRol, Documentos, Rol, HistorialDocumentos
from .forms import UsuarioForm, LoginForm, DocumentoForm, DOCUMENTOS_POR_ROL, EditarPerfil, es_menor
from .decorators import bloqueo_documentos_completos, rol_requerido
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
                    num_identificacion=documento,
                    contrasena=contrasena,
                )

                if not usuario.estado:
                    messages.error(
                        request,
                        "Tu cuenta se encuentra Inactiva. Comunicate con el Administrador."
                    )
                    return redirect("login")

                roles = DetallesUsuarioRol.objects.filter(
                    id_usuario=usuario
                ).select_related("id_rol")

                lista_roles = [
                    r.id_rol.rol_usuario
                    for r in roles
                ]

                # ===== SESIONES =====

                request.session["usuario_id"] = usuario.id_usuario

                request.session["nombre"] = usuario.nombre_completo

                request.session["foto"] = usuario.foto_perfil.url if usuario.foto_perfil else ""

                request.session["roles"] = ", ".join(lista_roles)


                if "Administrador" in lista_roles:

                    return redirect("dashboard")

                # ===== DOCUMENTOS =====

                documentos_requeridos = set()

                for rol in lista_roles:

                    if rol == "Jugador" and es_menor(usuario):

                        documentos_requeridos.update(
                            DOCUMENTOS_POR_ROL.get(
                                "JugadorMenor",
                                []
                            )
                        )

                    else:

                        documentos_requeridos.update(
                            DOCUMENTOS_POR_ROL.get(
                                rol,
                                []
                            )
                        )

                documentos_subidos = set(

                    Documentos.objects.filter(
                        usuario=usuario
                    ).values_list(
                        'tipo_documento',
                        flat=True
                    )

                )

                faltantes = (
                    documentos_requeridos -
                    documentos_subidos
                )


                if faltantes:

                    return redirect(
                        "mi_perfil",
                        usuario.id_usuario
                    )

                return redirect("dashboard")

            except Usuario.DoesNotExist:

                messages.error(
                    request,
                    "Documento o contraseña incorrectos"
                )

                return redirect("login")

    return render(request, "login.html", {
        "form": form
    })

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
def documentos(request, id, categoria=None):

    usuario = Usuario.objects.get(id_usuario=id)
    documentos = Documentos.objects.filter(usuario=usuario)
    historial = HistorialDocumentos.objects.filter(usuario=usuario).order_by('-fecha_eliminacion')

    usuario_sesion_id = request.session.get("usuario_id")
    roles_sesion = request.session.get("roles", [])

    if "Administrador" not in roles_sesion and usuario_sesion_id != id:
        return redirect('error400')

    roles_usuario = usuario.roles.values_list('rol_usuario', flat=True)

    documentos_requeridos = set()
    categorias_permitidas = set()

    # 🔥 ROLES → DOCUMENTOS + CATEGORIAS PERMITIDAS
    for rol in roles_usuario:
        if rol == "Jugador" and es_menor(usuario):
            docs = DOCUMENTOS_POR_ROL.get("JugadorMenor", [])
        else:
            docs = DOCUMENTOS_POR_ROL.get(rol, [])

        documentos_requeridos.update(docs)

        for doc in docs:
            cat = Documentos.DOCUMENTOS_CATEGORIA_MAP.get(doc)
            if cat:
                categorias_permitidas.add(cat)

    # 🔥 FILTRO POR CATEGORIA (URL)
    if categoria:
        categoria = categoria.upper()
        documentos = documentos.filter(categoria=categoria)

    documentos_subidos = set(
        documentos.values_list('tipo_documento', flat=True)
    )

    faltantes = documentos_requeridos - documentos_subidos
    request.session["docs_completos"] = len(faltantes) == 0

    # 🔥 FILTRO DE FALTANTES POR CATEGORIA
    if categoria:
        faltantes = {
            doc for doc in faltantes
            if Documentos.DOCUMENTOS_CATEGORIA_MAP.get(doc) == categoria
        }

    dict_documentos = dict(Documentos.DOCUMENTACION)

    faltantes_display = [
        dict_documentos.get(doc, doc)
        for doc in faltantes
    ]

    total_requeridos = len(documentos_requeridos)
    total_subidos = len(documentos_subidos)

    progreso = int((total_subidos / total_requeridos) * 100) if total_requeridos > 0 else 0

    # 🔥 AGRUPAR SOLO CATEGORÍAS PERMITIDAS
    docs_por_categoria = {}

    for doc in documentos:
        cat = doc.categoria

        if cat not in categorias_permitidas:
            continue

        if cat not in docs_por_categoria:
            docs_por_categoria[cat] = []

        docs_por_categoria[cat].append(doc)

    # 🔥 FILTRO FINAL SI VIENE CATEGORÍA
    if categoria:
        docs_por_categoria = {
            categoria: docs_por_categoria.get(categoria, [])
        }

    # FORMULARIO
    if request.method == 'POST':
        formulario = DocumentoForm(
            request.POST,
            request.FILES,
            usuario=usuario,
            categoria=categoria
        )

        if formulario.is_valid():
            doc = formulario.save(commit=False)

            doc.usuario = usuario

            if categoria:
                doc.categoria = categoria

            doc.estado = "PENDIENTE"
            doc.save()

            messages.success(request, "Documento subido correctamente")
            return redirect('documentos', id=usuario.id_usuario)

        else:
            for field, errors in formulario.errors.items():
                for error in errors:
                    messages.error(request, f"Error: {error}")

    else:
        formulario = DocumentoForm(
            usuario=usuario,
            categoria=categoria,
            categorias_permitidas=categorias_permitidas
        )

    documentos_categoria_json = json.dumps({
        doc: cat
        for doc, cat in Documentos.DOCUMENTOS_CATEGORIA_MAP.items()
        if doc in documentos_requeridos
    })

    return render(request, 'usuarios/documentos.html', {
        'formulario': formulario,
        'usuario': usuario,
        'documentos': documentos,
        'faltantes': faltantes_display,
        'progreso': progreso,
        'total_subidos': total_subidos,
        'total_requeridos': total_requeridos,
        'docs_por_categoria': docs_por_categoria,
        'documentos_categoria_json': documentos_categoria_json,
        'categoria_actual': categoria,
        'categorias_permitidas': categorias_permitidas,
        'historial': historial
    })

def cambiar_estado_documento(request, id):
    doc = get_object_or_404(Documentos, id_archivo=id)

    if request.method == "POST":
        estado = request.POST.get("estado")

        # 🔴 DEVUELTO → guardar historial + borrar
        if estado == "DEVUELTO":
            observacion = request.POST.get("observacion_rechazo")

            if not observacion or len(observacion.strip()) < 3:
                messages.error(request, "Debe escribir una observación")
                return redirect(request.META.get('HTTP_REFERER'))

            # 🔥 GUARDAR HISTORIAL ANTES DE BORRAR
            HistorialDocumentos.objects.create(
                usuario=doc.usuario,
                tipo_documento=doc.tipo_documento,
                nombre=doc.nombre,
                observaciones=doc.observaciones,
                observaciones_rechazo=observacion.strip()
            )

            # 🔥 BORRAR ARCHIVO FÍSICO
            if doc.archivo:
                doc.archivo.delete(save=False)

            doc.delete()

            messages.success(request, "Documento eliminado y guardado en historial")

            return redirect("documentos", id=doc.usuario.id_usuario)

        # 🟢 OTROS ESTADOS
        elif estado in ["APROBADO", "PENDIENTE"]:
            doc.estado = estado
            doc.save()

            messages.success(request, "Estado actualizado correctamente")

    return redirect(request.META.get('HTTP_REFERER'))

def historial_documentos(request, id):
    usuario = get_object_or_404(Usuario, id_usuario=id)

    historial = HistorialDocumentos.objects.filter(usuario=usuario).order_by('-fecha_eliminacion')

    return render(request, "usuarios/historial_modal.html", {
        "historial": historial,
        "usuario": usuario
    })

def borrar_documento(request, id):
    usuario_sesion_id = request.session.get("usuario_id")
    roles_sesion = request.session.get("roles", [])
    if not usuario_sesion_id:
        return redirect("login")
    documento = get_object_or_404(Documentos, id_archivo=id)
    usuario_id = documento.usuario.id_usuario
    if documento.usuario.id_usuario == usuario_sesion_id or "Administrador" in roles_sesion:
        if documento.archivo:
            documento.archivo.delete(save=False)
        documento.delete()
        messages.success(request, "Documento eliminado correctamente")
    else:
        messages.error(request, "No tienes permiso")
    return redirect("documentos", id=usuario_id)

@rol_requerido(["Administrador"])
def crear_usuario(request):
    url = "https://www.apicountries.com/countries"
    response = requests.get(url)
    data = response.json()
    paises = sorted([
        {
            'codigo': p['alpha2Code'],
            'nombre': p['name']
        }
        for p in data if p.get('alpha2Code') and p.get('name')
    ], key=lambda x: x['nombre'])
    formulario = UsuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        usuario = formulario.save(commit=False)
        usuario.lugar_nacimiento = request.POST.get('lugar_nacimiento')
        usuario.save()
        formulario.save_m2m()
        roles = usuario.roles.all()
        nombres_roles = ", ".join([rol.rol_usuario for rol in roles])
        print("Correo del usuario:", usuario.correo)
        print("Roles:", nombres_roles)
        send_mail(
            'Usuario creado - Credenciales de Acceso',
            f'''
            Hola {usuario.nombre_completo},
            Tu cuenta ha sido creada correctamente.
            📧 Usuario: {usuario.num_identificacion}
            🔑 Contraseña: {usuario.contrasena}
            👤 Roles: {nombres_roles}
            Bienvenido al sistema.
            ''',
            'administrativo@codegol.com',
            [usuario.correo],
            fail_silently=False,
        )
        return redirect('documentos', id=usuario.id_usuario)
    return render(request, "usuarios/usuario_form.html", {'formulario': formulario,'paises': paises})

def consulta_especifica_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    roles_usuario = list(usuario.roles.values_list('id_rol', flat=True))
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
    url = "https://www.apicountries.com/countries"
    response = requests.get(url)
    data = response.json()
    pais_nombre = usuario.lugar_nacimiento  
    for p in data:
        if p.get('alpha2Code') == usuario.lugar_nacimiento:
            pais_nombre = p.get('name')
            break
    return render(request, "usuarios/especifica.html", {'usuario': usuario,'roles_usuario': roles_usuario,'pais_nombre': pais_nombre})

def editar_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    url = "https://www.apicountries.com/countries"
    response = requests.get(url)
    data = response.json()
    paises = sorted([
        {
            'codigo': p['alpha2Code'],
            'nombre': p['name']
        }
        for p in data if p.get('alpha2Code') and p.get('name')
    ], key=lambda x: x['nombre'])
    formulario = UsuarioForm(request.POST or None, request.FILES or None, instance=usuario)
    usuario_sesion_id = request.session.get("usuario_id")
    roles = request.session.get("roles", [])
    if "Administrador" not in roles and usuario_sesion_id != id:
        return redirect('error400')
    if formulario.is_valid() and request.POST:
        usuario = formulario.save(commit=False)
        usuario.lugar_nacimiento = request.POST.get('lugar_nacimiento')  
        usuario.save()
        formulario.save_m2m()
        return redirect('usuario')
    return render(request, "usuarios/usuario_form.html", {'formulario': formulario,'paises': paises })

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
