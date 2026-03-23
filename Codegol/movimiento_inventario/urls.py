from django.urls import path
from . import views

urlpatterns = [
    path('inventario/<int:id_inventario>/', views.lista_movimientos, name='lista_movimientos'),
    path('crear/<int:id_inventario>/', views.crear_movimiento, name='crear_movimiento'),
    path('movimientos/actualizar/', views.actualizar_observaciones, name='actualizar_observaciones'),
    
]

