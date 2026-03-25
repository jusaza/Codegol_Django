from django.shortcuts import render, get_object_or_404, redirect
from .models import Matricula
from usuario.models import Usuario
from django.shortcuts import render, get_object_or_404, redirect


# LISTAR
def lista_matricula(request):
    query = request.GET.get('q')

    if query:
        matriculas = Matricula.objects.filter(
            id_jugador__nombre_completo__icontains=query,
            estado=True
        )
    else:
        matriculas = Matricula.objects.filter(estado=True)

    return render(request, 'matricula/lista.html', {
        'matriculas': matriculas,
        'query': query
    })


# CREAR
def crear_matricula(request):
    usuarios = Usuario.objects.all()

    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        fecha_matricula = request.POST.get('fecha_matricula')
        nivel = request.POST.get('nivel')
        observaciones = request.POST.get('observaciones')
        id_jugador = request.POST.get('id_jugador')

        if not id_jugador:
            return render(request, 'matricula/crear.html', {
                'usuarios': usuarios,
                'error': 'Debe seleccionar un jugador'
            })

        # 🔥 CORRECCIÓN
        jugador = Usuario.objects.get(id_usuario=id_jugador)

        Matricula.objects.create(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            fecha_matricula=fecha_matricula,
            nivel=nivel,
            observaciones=observaciones,
            estado=True,
            id_jugador=jugador
        )

        return redirect('lista_matricula')

    return render(request, 'matricula/crear.html', {
        'usuarios': usuarios
    })


# EDITAR
def editar_matricula(request, id):
    matricula = get_object_or_404(Matricula, id=id)

    if request.method == 'POST':
        matricula.fecha_inicio = request.POST['fecha_inicio']
        matricula.fecha_fin = request.POST['fecha_fin']
        matricula.fecha_matricula = request.POST['fecha_matricula']
        matricula.nivel = request.POST['nivel']
        matricula.observaciones = request.POST['observaciones']

        matricula.save()

        # 🔥 ESTA ES LA CLAVE
        return redirect('/matricula/')  

    return render(request, 'matricula/editar.html', {
        'matricula': matricula
    })



# ELIMINAR
def eliminar_matricula(request, id):
    matricula = get_object_or_404(Matricula, pk=id)
    matricula.estado = False
    matricula.save()

    return redirect('lista_matricula')
