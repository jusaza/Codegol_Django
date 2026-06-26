from django.db.models import Sum
from django.shortcuts import redirect, render
import json

from asistencia.models import Asistencia
from categoria.models import Categoria
from entrenamientos.models import Entrenamiento
from inventario.models import Inventario
from matricula.models import HistorialCategoria, Matricula
from pago.models import Pago
from sesion_entrenamiento.models import SesionEntrenamiento
from usuario.decorators import bloqueo_documentos_completos
from usuario.models import Documentos, Usuario


def inicio(request):
    return render(request, 'inicio.html')


def _roles_sesion(request):
    roles = request.session.get("roles", "")
    return {
        "es_admin": "Administrador" in roles,
        "es_entrenador": "Entrenador" in roles,
        "es_jugador": "Jugador" in roles,
    }


def _contexto_admin():
    usuarios_total = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(estado=True).count()
    pagos = Pago.objects.all()
    pagos_total = pagos.count()
    pagos_cancelados = pagos.filter(cancelado=True).count()
    pagos_pendientes = pagos.filter(cancelado=False).count()
    total_recaudo = pagos.aggregate(total=Sum('valor_total'))['total'] or 0
    documentos_total = Documentos.objects.count()
    documentos_por_categoria = {
        "legal": Documentos.objects.filter(categoria="LEGAL").count(),
        "medico": Documentos.objects.filter(categoria="MEDICO").count(),
        "academico": Documentos.objects.filter(categoria="ACADEMICO").count(),
        "deportivo": Documentos.objects.filter(categoria="DEPORTIVO").count(),
        "personal": Documentos.objects.filter(categoria="PERSONAL").count(),
    }
    matriculas_total = Matricula.objects.filter(estado=True).count()
    niveles = {
        "Alto": Matricula.objects.filter(nivel="Alto", estado=True).count(),
        "Medio": Matricula.objects.filter(nivel="Medio", estado=True).count(),
        "Bajo": Matricula.objects.filter(nivel="Bajo", estado=True).count(),
    }
    inventario_total = Inventario.objects.count()
    entrenamientos_total = Entrenamiento.objects.count()

    documentos_pendientes_qs = Documentos.objects.filter(
        estado="PENDIENTE",
    ).select_related("usuario").order_by("-fecha_subida")

    return {
        "rol_dashboard": "administrador",
        "titulo_dashboard": "Panel administrativo",
        "subtitulo_dashboard": "Control general del sistema",

        "usuarios_total": usuarios_total,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_total - usuarios_activos,
        "pagos_total": pagos_total,
        "pagos_cancelados": pagos_cancelados,
        "pagos_pendientes": pagos_pendientes,
        "total_recaudo": total_recaudo,
        "documentos_total": documentos_total,
        "documentos": documentos_por_categoria,
        "matriculas_total": matriculas_total,
        "niveles": niveles,
        "inventario_total": inventario_total,
        "entrenamientos_total": entrenamientos_total,

        "documentos_pendientes": documentos_pendientes_qs,
        "documentos_pendientes_total": documentos_pendientes_qs.count(),

        "mostrar_kpis_admin": True,
        "mostrar_revision_documentos": True,
        "mostrar_filtro_entrenador": True,
        "mostrar_boton_entrenamiento": True,
        "mostrar_grafico_general": True,
        "mostrar_grafico_finanzas": True,
        "mostrar_grafico_documentos": True,
        "mostrar_grafico_niveles": True,

        "general_chart_labels": json.dumps([
            "Usuarios",
            "Documentos",
            "Pagos",
            "Matrículas",
            "Inventario",
            "Entrenamientos",
        ]),
        "general_chart_data": json.dumps([
            usuarios_total,
            documentos_total,
            pagos_total,
            matriculas_total,
            inventario_total,
            entrenamientos_total,
        ]),
        "finance_chart_data": json.dumps([
            pagos_total - pagos_pendientes,
            pagos_pendientes,
            pagos_cancelados,
        ]),
    }


def _contexto_entrenador(usuario_id):
    sesiones = SesionEntrenamiento.objects.filter(
        id_entrenador_id=usuario_id,
        estado=True,
    )
    matriculas_activas = Matricula.objects.filter(estado=True).count()
    entrenamientos_activos = Entrenamiento.objects.filter(estado=True).count()
    inventario_activo = Inventario.objects.filter(estado=True).count()
    niveles = {
        "Alto": Matricula.objects.filter(nivel="Alto", estado=True).count(),
        "Medio": Matricula.objects.filter(nivel="Medio", estado=True).count(),
        "Bajo": Matricula.objects.filter(nivel="Bajo", estado=True).count(),
    }

    return {
        "rol_dashboard": "entrenador",
        "titulo_dashboard": "Panel de entrenador",
        "subtitulo_dashboard": "Tus sesiones, jugadores y actividades",

        "sesiones_total": sesiones.count(),
        "matriculas_activas": matriculas_activas,
        "entrenamientos_activos": entrenamientos_activos,
        "inventario_activo": inventario_activo,
        "niveles": niveles,
        "entrenador_id": usuario_id,

        "mostrar_kpis_entrenador": True,
        "mostrar_filtro_entrenador": False,
        "mostrar_boton_entrenamiento": True,
        "mostrar_grafico_general": True,
        "mostrar_grafico_finanzas": False,
        "mostrar_grafico_documentos": False,
        "mostrar_grafico_niveles": True,

        "general_chart_labels": json.dumps([
            "Mis sesiones",
            "Matrículas",
            "Entrenamientos",
            "Inventario",
        ]),
        "general_chart_data": json.dumps([
            sesiones.count(),
            matriculas_activas,
            entrenamientos_activos,
            inventario_activo,
        ]),
    }


def _contexto_jugador(usuario_id):
    matriculas = Matricula.objects.filter(
        id_jugador_id=usuario_id,
        estado=True,
    )
    matricula_activa = matriculas.first()
    pagos = Pago.objects.filter(id_matricula__in=matriculas)
    pagos_total = pagos.count()
    pagos_registrados = pagos.filter(cancelado=False).count()
    pagos_cancelados = pagos.filter(cancelado=True).count()
    documentos = Documentos.objects.filter(usuario_id=usuario_id)
    documentos_aprobados = documentos.filter(estado="APROBADO").count()
    documentos_pendientes = documentos.filter(estado="PENDIENTE").count()
    asistencias = Asistencia.objects.filter(
        id_matricula__in=matriculas,
        tipo_asistencia="asiste",
    ).count()
    inasistencias = Asistencia.objects.filter(
        id_matricula__in=matriculas,
        tipo_asistencia="inasiste",
    ).count()

    historial_categoria = HistorialCategoria.objects.filter(
        id_matricula__in=matriculas,
        estado=True,
    ).select_related("id_categoria").first()

    nivel_jugador = matricula_activa.nivel if matricula_activa else "Sin nivel"
    categoria_jugador = (
        historial_categoria.id_categoria.nombre_categoria
        if historial_categoria else "Sin categoría"
    )
    categoria_jugador_id = (
        historial_categoria.id_categoria_id
        if historial_categoria else ""
    )

    return {
        "rol_dashboard": "jugador",
        "titulo_dashboard": "Mi panel",
        "subtitulo_dashboard": "Tu información deportiva y académica",

        "matricula_activa": matricula_activa,
        "nivel_jugador": nivel_jugador,
        "categoria_jugador": categoria_jugador,
        "categoria_jugador_id": categoria_jugador_id,
        "pagos_total": pagos_total,
        "pagos_pendientes": pagos_registrados,
        "pagos_registrados": pagos_registrados,
        "pagos_cancelados_usuario": pagos_cancelados,
        "documentos_aprobados": documentos_aprobados,
        "documentos_pendientes_usuario": documentos_pendientes,
        "asistencias_total": asistencias,
        "inasistencias_total": inasistencias,

        "mostrar_kpis_jugador": True,
        "mostrar_filtro_entrenador": False,
        "mostrar_filtro_entrenamiento": False,
        "mostrar_boton_entrenamiento": False,
        "mostrar_grafico_general": True,
        "mostrar_grafico_finanzas": True,
        "mostrar_grafico_documentos": False,
        "mostrar_grafico_niveles": False,

        "general_chart_labels": json.dumps([
            "Asistencias",
            "Inasistencias",
            "Documentos",
            "Pagos",
        ]),
        "general_chart_data": json.dumps([
            asistencias,
            inasistencias,
            documentos.count(),
            pagos_total,
        ]),
        "finance_chart_data": json.dumps([
            pagos_registrados,
            pagos_cancelados,
        ]),
    }


@bloqueo_documentos_completos
def dashboard(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    roles = _roles_sesion(request)
    usuario_id = request.session.get("usuario_id")

    context = {
        "nombre_usuario": request.session.get("nombre", ""),
        "entrenamientos": Entrenamiento.objects.filter(estado=True),
        "categorias": Categoria.objects.filter(estado=True),
        "entrenadores": Usuario.objects.filter(
            usuario__id_rol__rol_usuario="Entrenador",
            estado=True,
        ).distinct(),
    }

    if roles["es_admin"]:
        context.update(_contexto_admin())
    elif roles["es_entrenador"]:
        context.update(_contexto_entrenador(usuario_id))
    elif roles["es_jugador"]:
        context.update(_contexto_jugador(usuario_id))
    else:
        context.update({
            "rol_dashboard": "usuario",
            "titulo_dashboard": "Panel de inicio",
            "subtitulo_dashboard": "Bienvenido al sistema",
            "mostrar_grafico_general": False,
            "mostrar_grafico_finanzas": False,
            "mostrar_grafico_documentos": False,
            "mostrar_grafico_niveles": False,
        })

    context.update(roles)
    return render(request, "pagina_original.html", context)


def nosotros(request):
    return render(request, 'nosotros.html')


def servicios(request):
    return render(request, 'servicios.html')


def pagina_original(request):
    return redirect("dashboard")


def error400(request):
    return render(request, '404.html')
