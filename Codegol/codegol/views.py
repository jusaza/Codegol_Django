from django.shortcuts import render

from . import views 
from django.shortcuts import render

from usuario.models import Usuario, Documentos
from pago.models import Pago
from matricula.models import Matricula, HistorialCategoria
from inventario.models import Inventario
from entrenamientos.models import Entrenamiento


from django.shortcuts import render
from django.db.models import Sum, Avg, Max, Min

from django.db.models import Sum, Avg, Max, Min
from django.shortcuts import render

def inicio(request):
    return render(request, 'inicio.html')

def dashboard(request):
    usuarios_total = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(estado=True).count()
    usuarios_inactivos = usuarios_total - usuarios_activos

    porcentaje_usuarios_activos = (
        (usuarios_activos / usuarios_total * 100) if usuarios_total > 0 else 0
    )
    pagos = Pago.objects.all()
    pagos_total = pagos.count()
    pagos_cancelados = pagos.filter(cancelado=True).count()
    pagos_pendientes = pagos.filter(cancelado=False).count()
    total_recaudo = pagos.aggregate(total=Sum('valor_total'))['total'] or 0
    recaudo_confirmado = pagos.filter(cancelado=False).aggregate(total=Sum('valor_total'))['total'] or 0
    recaudo_pendiente = pagos.filter(cancelado=True).aggregate(total=Sum('valor_total'))['total'] or 0
    promedio_pago = pagos.aggregate(avg=Avg('valor_total'))['avg'] or 0
    pago_maximo = pagos.aggregate(max=Max('valor_total'))['max'] or 0
    pago_minimo = pagos.aggregate(min=Min('valor_total'))['min'] or 0
    pagos_altos = pagos.filter(valor_total__gte=promedio_pago).count()
    documentos_total = Documentos.objects.count()
    documentos_por_categoria = {
        "legal": Documentos.objects.filter(categoria="LEGAL").count(),
        "medico": Documentos.objects.filter(categoria="MEDICO").count(),
        "academico": Documentos.objects.filter(categoria="ACADEMICO").count(),
        "deportivo": Documentos.objects.filter(categoria="DEPORTIVO").count(),
        "personal": Documentos.objects.filter(categoria="PERSONAL").count(),
    }
    matriculas_total = Matricula.objects.count()
    matriculas_activas = Matricula.objects.filter(estado=True).count()
    matriculas_inactivas = matriculas_total - matriculas_activas
    porcentaje_matriculas = (
        (matriculas_activas / matriculas_total * 100) if matriculas_total > 0 else 0
    )
    niveles = {
        "Alto": Matricula.objects.filter(nivel="Alto").count(),
        "Medio": Matricula.objects.filter(nivel="Medio").count(),
        "Bajo": Matricula.objects.filter(nivel="Bajo").count(),
    }
    inventario_total = Inventario.objects.count()
    inventario_activo = Inventario.objects.filter(estado=True).count()
    inventario_inactivo = inventario_total - inventario_activo
    entrenamientos_total = Entrenamiento.objects.count()
    entrenamientos_activos = Entrenamiento.objects.filter(estado=True).count()
    entrenamientos_inactivos = entrenamientos_total - entrenamientos_activos
    context = {
        "usuarios_total": usuarios_total,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_inactivos,
        "porcentaje_usuarios_activos": porcentaje_usuarios_activos,

        "pagos_total": pagos_total,
        "pagos_cancelados": pagos_cancelados,
        "pagos_pendientes": pagos_pendientes,

        "total_recaudo": total_recaudo,
        "recaudo_confirmado": recaudo_confirmado,
        "recaudo_pendiente": recaudo_pendiente,

        "promedio_pago": promedio_pago,
        "pago_maximo": pago_maximo,
        "pago_minimo": pago_minimo,
        "pagos_altos": pagos_altos,

        "documentos_total": documentos_total,
        "documentos": documentos_por_categoria,

        "matriculas_total": matriculas_total,
        "matriculas_activas": matriculas_activas,
        "matriculas_inactivas": matriculas_inactivas,
        "porcentaje_matriculas": porcentaje_matriculas,

        "niveles": niveles,

        "inventario_total": inventario_total,
        "inventario_activo": inventario_activo,
        "inventario_inactivo": inventario_inactivo,
        
        "entrenamientos_total": entrenamientos_total,
        "entrenamientos_activos": entrenamientos_activos,
        "entrenamientos_inactivos": entrenamientos_inactivos,
    }

    return render(request, "pagina_original.html", context)

def nosotros(request):
    return render(request, 'nosotros.html')

def servicios(request):
    return render(request, 'servicios.html')
    
def pagina_original(request):
    return render(request, 'pagina_original.html')

def error400(request):
    return render(request, '404.html')
