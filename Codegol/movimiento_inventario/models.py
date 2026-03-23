from django.db import models
from inventario.models import Inventario
from usuario.models import Usuario  # ajusta si tu modelo se llama diferente

class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('devolucion', 'Devolución'),
    ]

    id_movimiento = models.AutoField(primary_key=True)
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_sesion = models.IntegerField(null=True, blank=True)  # simple por ahora

    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'movimiento_inventario'

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.inventario.nombre_articulo}"
