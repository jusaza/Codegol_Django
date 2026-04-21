from django.db import models

class Posicion(models.Model):

    id_posicion = models.AutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    class Meta:
        db_table = "posicion"

    def __str__(self):
        return self.nombre