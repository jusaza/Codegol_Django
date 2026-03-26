from django.db import models
from usuario.models import Usuario
from categoria.models import Categoria

class Matricula(models.Model):

    NIVEL_CHOICES = [
        ('Alto', 'Alto'),
        ('Medio', 'Medio'),
        ('Bajo', 'Bajo'),
    ]

    estado = models.BooleanField(default=True)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_matricula = models.DateField(auto_now_add=True)

    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES
    )

    observaciones = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    id_jugador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='matriculas',
        db_column='id_jugador' 
    )

    class Meta:
        db_table = "matricula"  

    def __str__(self):
        return f"Matricula {self.id}"



class HistorialCategoria(models.Model):
    id_historial = models.AutoField(primary_key=True)

    id_matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        db_column='id_matricula'
    )

    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        db_column='id_categoria'
    )

    fecha_registro = models.DateField()

    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'historial_categoria'

    def __str__(self):
        return f"Historial {self.id_historial}"