from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pagos, name='lista_pagos'),
    path('crear/', views.crear_pago, name='crear_pago'),
    path('editar/<int:id>/', views.editar_pago, name='editar_pago'),
    path('cancelar/<int:id>/', views.cancelar_pago, name='cancelar_pago'),
    path('conceptos/valores/', views.actualizar_valores_conceptos, name='actualizar_valores_conceptos'),
    path('reporte/pagos/pdf/', views.reporte_pagos_pdf, name='reporte_pagos_pdf'),
]