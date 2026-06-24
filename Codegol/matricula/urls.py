from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_matricula, name='lista_matricula'),
    path('crear/', views.crear_matricula, name='crear_matricula'),
    path('editar/<int:id>/', views.editar_matricula, name='editar_matricula'),
    path('eliminar/<int:id>/', views.eliminar_matricula, name='eliminar_matricula'),
    path('asignar_categoria/<int:id>/', views.asignar_categoria, name='asignar_categoria'),
    path('historial_categoria/<int:id>/', views.ver_historial_categoria, name='historial_categoria'),
    path('certificado/<int:id>/', views.generar_certificado, name='certificado'),
    path('exportar-excel/', views.exportar_matriculas_excel, name='exportar_excel'),
    path('modal-filtro-excel/',views.modal_filtro_excel,name='modal_filtro_excel'),
    path('carga-masiva/',views.cargar_matriculas_csv,name='carga_masiva_matricula'),
    path(
    'inactivos/',
    views.lista_matricula_inactivos,
    name='lista_matricula_inactivos'
),

path(
    'activar/<int:id>/',
    views.activar_matricula,
    name='activar_matricula'
),
]
