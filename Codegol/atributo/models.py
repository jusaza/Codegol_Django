from django.db import models

class Atributo(models.Model):

    id_atributo = models.AutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    descripcion = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "atributo"

    def __str__(self):
        return self.nombre