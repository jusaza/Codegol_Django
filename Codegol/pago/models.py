from django.db import models

class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id_matricula)


class Pago(models.Model):
    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Otro', 'Otro'),
    ]

    concepto_pago = models.CharField(max_length=100)
    fecha_pago = models.DateField()
    metodo_pago = models.CharField(max_length=20, choices=METODOS)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    valor_total = models.FloatField()
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)

    def __str__(self):
        return self.concepto_pago