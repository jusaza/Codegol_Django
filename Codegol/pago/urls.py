from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pagos, name='lista_pagos'),
    path('crear/', views.crear_pago, name='crear_pago'),
    path('editar/<int:id>/', views.editar_pago, name='editar_pago'),
    path('eliminar/<int:id>/', views.eliminar_pago, name='eliminar_pago'),
]