from django.db import models

# Create your models here.
class Inventario(models.Model):
    id_inventario = models.AutoField(primary_key=True)
    nombre_articulo = models.CharField(max_length=100,
        unique=True) 
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    estado = models.BooleanField()

    class Meta:
        db_table = 'inventario'

    def __str__(self):
        return self.nombre_articulo