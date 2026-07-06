from django.db import models
from matricula.models import Matricula


class Pago(models.Model):
    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Otro', 'Otro'),
    ]

    CONCEPTOS = [
        ('Matrícula', 'Matrícula'),
        ('Mensualidad', 'Mensualidad'),
        ('Uniformes', 'Uniformes'),
        ('Daños a la propiedad', 'Daños a la propiedad'),
        ('Torneos', 'Torneos'),
        ('Implementos deportivos', 'Implementos deportivos'),
        ('Transporte', 'Transporte'),
        ('Otros', 'Otros'),
    ]

    concepto_pago = models.CharField(max_length=100)
    fecha_pago = models.DateField()
    metodo_pago = models.CharField(max_length=20, choices=METODOS)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    valor_total = models.FloatField()
    cancelado = models.BooleanField(default=False)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)

    def __str__(self):
        return self.concepto_pago