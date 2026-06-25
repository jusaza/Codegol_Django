from django.db import models
from actividad.models import Actividad
from atributo.models import Atributo

class ActividadAtributo(models.Model):

    id = models.AutoField(primary_key=True)

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='actividad_atributos'
    )

    atributo = models.ForeignKey(
        Atributo,
        on_delete=models.CASCADE,
        related_name='atributo_actividades'
    )

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1
    )

    class Meta:
        db_table = "actividad_atributo"
        unique_together = ('actividad', 'atributo')

    def __str__(self):
        return f"{self.actividad} - {self.atributo}"