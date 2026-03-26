from django.shortcuts import render
from django.db.models import Avg, F, FloatField, ExpressionWrapper
from matricula.models import Matricula

from django.shortcuts import render
from django.db.models import Avg, F, FloatField, ExpressionWrapper
from matricula.models import Matricula

def lista_jugadores(request):
    query = request.GET.get('q')

    jugadores = Matricula.objects.filter(
        estado=True
    ).select_related('id_jugador').annotate(

        # 🔹 Promedios por habilidad
        prom_defensa=Avg('asistencia__rendimiento__defensa'),
        prom_pase=Avg('asistencia__rendimiento__pase'),
        prom_regate=Avg('asistencia__rendimiento__regate'),
        prom_tecnica=Avg('asistencia__rendimiento__tecnica'),
        prom_velocidad=Avg('asistencia__rendimiento__velocidad'),
        prom_tiro=Avg('asistencia__rendimiento__potencia_tiro'),

    ).annotate(
        promedio_final=ExpressionWrapper(
            (
                F('prom_defensa') +
                F('prom_pase') +
                F('prom_regate') +
                F('prom_tecnica') +
                F('prom_velocidad') +
                F('prom_tiro')
            ) / 6,
            output_field=FloatField()
        )
    )

    # 🔎 BUSCADOR
    if query:
        jugadores = jugadores.filter(
            id_jugador__num_identificacion__icontains=query
        )

    # 🔤 ORDEN
    jugadores = jugadores.order_by('id_jugador__nombre_completo')

    return render(request, 'rendimiento/lista.html', {
        'jugadores': jugadores,
        'query': query
    })