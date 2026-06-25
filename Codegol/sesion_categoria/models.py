from django.db import models

from sesion_entrenamiento.models import SesionEntrenamiento
from categoria.models import Categoria


class SesionCategoria(models.Model):

    id_sesion_categoria = models.AutoField(
        primary_key=True
    )

    id_sesion = models.ForeignKey(
        SesionEntrenamiento,
        on_delete=models.CASCADE
    )

    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "sesion_categoria"

        unique_together = (
            "id_sesion",
            "id_categoria"
        )

    def __str__(self):
        return (
            f"{self.id_sesion} - "
            f"{self.id_categoria}"
        )
