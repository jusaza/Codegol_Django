from django.urls import path
from . import views

urlpatterns = [
    path('inventario/<int:id_inventario>/', views.lista_movimientos, name='lista_movimientos'),
    path('crear/<int:id_inventario>/', views.crear_movimiento, name='crear_movimiento'),
    path('movimientos/actualizar/', views.actualizar_observaciones, name='actualizar_observaciones'),
    path('salidas/sesion/<int:id_sesion>/', views.salidas_sesion, name='salidas_sesion'),
    path('devolver/<int:id_movimiento>/', views.crear_devolucion, name='crear_devolucion'),
    
    
]

