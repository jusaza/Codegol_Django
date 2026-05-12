from django.db import models
from sesion_entrenamiento.models import SesionEntrenamiento
from actividad.models import Actividad

class SesionActividad(models.Model):

    id = models.AutoField(primary_key=True)

    sesion = models.ForeignKey(
        SesionEntrenamiento,
        on_delete=models.CASCADE,
        related_name='sesion_actividades'
    )

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE
    )

    orden = models.IntegerField()
    duracion_min = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "sesion_actividad"
