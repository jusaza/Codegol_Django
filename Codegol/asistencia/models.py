from django.db import models
from sesion_entrenamiento.models import SesionEntrenamiento
from matricula.models import Matricula
from categoria.models import Categoria

class Asistencia(models.Model):
    TIPO_CHOICES = [
        ('asiste', 'Asiste'),
        ('inasiste', 'sInasiste'),
        ('llegada_tarde', 'Llegada tarde'),
    ]

    id_asistencia = models.AutoField(primary_key=True)

    id_sesion = models.ForeignKey(
        SesionEntrenamiento,
        on_delete=models.CASCADE,
        db_column='id_sesion'
    )

    id_matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        db_column='id_matricula',
        null = True
    )

    tipo_asistencia = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        blank=True,
    )

    justificacion = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.CharField(max_length=100, blank=True, null=True)

    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'asistencia'
