from django.db import models
from asistencia.models import Asistencia


class Rendimiento(models.Model):
    id_rendimiento = models.AutoField(primary_key=True)

    id_asistencia = models.OneToOneField(
        Asistencia,
        on_delete=models.CASCADE,
        db_column='id_asistencia'
    )

    # 🔥 ENUM DE POSICIONES
    POSICIONES = [
        ('POR', 'Portero'),
        ('DEF', 'Defensa'),
        ('MED', 'Mediocampista'),
        ('DEL', 'Delantero'),
        ('ND', 'No definido'),
    ]

    estado = models.BooleanField(default=True)

    # 🔥 CAMPOS (con mínimo 1)
    defensa = models.IntegerField(null=True, blank=True, default=1)
    pase = models.IntegerField(null=True, blank=True, default=1)
    regate = models.IntegerField(null=True, blank=True, default=1)
    tecnica = models.IntegerField(null=True, blank=True, default=1)
    velocidad = models.IntegerField(null=True, blank=True, default=1)
    potencia_tiro = models.IntegerField(null=True, blank=True, default=1)

    posicion = models.CharField(
        max_length=3,
        choices=POSICIONES,
        default='ND',
        null=True,
        blank=True
    )

    observaciones = models.CharField(max_length=100, null=True, blank=True)

    # 🔥 PROMEDIO (TE FALTABA EN EL MODELO)
    promedio = models.FloatField(null=True, blank=True, default=1)

    class Meta:
        db_table = 'rendimiento'

    

    def save(self, *args, **kwargs):
        valores = [
            self.defensa, self.pase, self.regate,
            self.tecnica, self.velocidad, self.potencia_tiro
        ]

        valores_validos = [v for v in valores if v is not None]

        if valores_validos:
            self.promedio = sum(valores_validos) / len(valores_validos)
        else:
            self.promedio = 1  # 👈 nunca 0, mínimo 1 como pediste

        super().save(*args, **kwargs)
