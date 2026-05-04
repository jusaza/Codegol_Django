from django.db import models
from posicion.models import Posicion
from actividad.models import Actividad

class PosicionActividad(models.Model):

    id = models.AutoField(primary_key=True)

    posicion = models.ForeignKey(
        Posicion,
        on_delete=models.CASCADE,
        related_name='posicion_actividades'
    )

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='actividad_posiciones'
    )

    obligatorio = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "posicion_actividad"
        unique_together = ('posicion', 'actividad')

    def __str__(self):
        return f"{self.posicion} - {self.actividad}"