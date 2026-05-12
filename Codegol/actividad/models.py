from django.db import models

class Actividad(models.Model):

    id_actividad = models.AutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "actividad"

    def __str__(self):
        return self.nombre