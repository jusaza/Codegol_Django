from django.db import models
from usuario.models import Usuario

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
