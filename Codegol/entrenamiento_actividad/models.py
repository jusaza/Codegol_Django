from django.db import models
from entrenamientos.models import Entrenamiento
from actividad.models import Actividad


class EntrenamientoActividad(models.Model):

    id = models.AutoField(primary_key=True)

    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name='entrenamiento_actividades'
    )

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='actividad_entrenamientos'
    )

    orden = models.IntegerField()

    duracion_min = models.IntegerField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "entrenamiento_actividad"
        unique_together = ('entrenamiento', 'actividad')

    def __str__(self):
        return f"{self.entrenamiento} - {self.actividad}"