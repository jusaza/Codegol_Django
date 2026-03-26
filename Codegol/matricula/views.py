from django.shortcuts import render, get_object_or_404, redirect
from .models import Matricula, HistorialCategoria
from usuario.models import Usuario
from categoria.models import Categoria
from datetime import date
from .models import Matricula, HistorialCategoria


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

    
    for m in matriculas:
        # Obtener el historial activo más reciente
        ultima = HistorialCategoria.objects.filter(
            id_matricula=m,
            estado=True
        ).order_by('-fecha_registro', '-id_historial').first() 

        if ultima:
            m.categoria_actual = ultima.id_categoria.nombre_categoria
        else:
            m.categoria_actual = "Sin categoría"

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
        matricula.fecha_inicio = request.POST.get('fecha_inicio')
        matricula.fecha_fin = request.POST.get('fecha_fin')
        matricula.fecha_matricula = request.POST.get('fecha_matricula')
        matricula.nivel = request.POST.get('nivel')
        matricula.observaciones = request.POST.get('observaciones')

        matricula.save()

        return redirect('lista_matricula')

    return render(request, 'matricula/editar.html', {
        'matricula': matricula
    })


def eliminar_matricula(request, id):
    matricula = get_object_or_404(Matricula, id=id)
    matricula.estado = False
    matricula.save()

    return redirect('lista_matricula')



def asignar_categoria(request, id):
    matricula = get_object_or_404(Matricula, id=id)
    categorias = Categoria.objects.filter(estado=True)

    if request.method == 'POST':
        id_categoria = request.POST.get('categoria')

        if id_categoria:
            HistorialCategoria.objects.create(
                id_matricula=matricula,
                id_categoria_id=id_categoria,
                fecha_registro=date.today(),
                estado=True
            )

        return redirect('lista_matricula')

    return render(request, 'matricula/asignar_categoria.html', {
        'matricula': matricula,
        'categorias': categorias
    })

def ver_historial_categoria(request, id):
    matricula = get_object_or_404(Matricula, id=id)

    historial = HistorialCategoria.objects.filter(
        id_matricula=matricula
    ).order_by('-fecha_registro')

    return render(request, 'matricula/historial_categoria.html', {
        'matricula': matricula,
        'historial': historial
    })