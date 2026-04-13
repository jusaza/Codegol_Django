from django.db import models

# Create your models here.
class Entrenamiento(models.Model):
    id_entrenamiento = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    estado = models.BooleanField()
    lugar = models.CharField(max_length=50)
    observaciones = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'entrenamiento'

    def __str__(self):
        return f"Entrenamiento {self.id_entrenamiento} - {self.lugar}"


