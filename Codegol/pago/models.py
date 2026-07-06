from django.db import models
from matricula.models import Matricula


class ConceptoPago(models.Model):
    NOMBRE_MATRICULA = 'Matrícula'
    NOMBRE_MENSUALIDAD = 'Mensualidad'
    NOMBRE_UNIFORME = 'Uniforme'
    NOMBRE_OTRO = 'Otro'

    CONCEPTOS_INICIALES = [
        NOMBRE_MATRICULA,
        NOMBRE_MENSUALIDAD,
        NOMBRE_UNIFORME,
        NOMBRE_OTRO,
    ]

    nombre = models.CharField(max_length=100, unique=True)
    valor = models.FloatField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Concepto de Pago'
        verbose_name_plural = 'Conceptos de Pago'
        ordering = ['id']

    def __str__(self):
        return self.nombre

    @property
    def es_otro(self):
        return self.nombre == self.NOMBRE_OTRO

    @classmethod
    def inicializar_conceptos(cls):
        for nombre in cls.CONCEPTOS_INICIALES:
            cls.objects.get_or_create(
                nombre=nombre,
                defaults={'valor': 0, 'activo': True},
            )


class Pago(models.Model):
    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Otro', 'Otro'),
    ]

    id_concepto = models.ForeignKey(
        ConceptoPago,
        on_delete=models.PROTECT,
        related_name='pagos',
    )
    concepto_pago = models.CharField(max_length=100)
    fecha_pago = models.DateField()
    metodo_pago = models.CharField(max_length=20, choices=METODOS)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    valor_total = models.FloatField()
    cancelado = models.BooleanField(default=False)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)

    def __str__(self):
        return self.concepto_pago
