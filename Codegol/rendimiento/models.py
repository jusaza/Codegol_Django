from django.db import models
from django.core.exceptions import ValidationError

from matricula.models import Matricula
from actividad.models import Actividad
from atributo.models import Atributo
from asistencia.models import Asistencia
from sesion_entrenamiento.models import SesionEntrenamiento
from posicion_actividad.models import PosicionActividad
from atributo_actividad.models import ActividadAtributo


class Rendimiento(models.Model):

    id_rendimiento = models.AutoField(primary_key=True)

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    sesion = models.ForeignKey(SesionEntrenamiento, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE)

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rendimiento_historico"

    def clean(self):

        # VALIDAR SOLO SI SE VA A GUARDAR VALOR
        if self.valor is not None:

            existe_asistencia = Asistencia.objects.filter(
                id_sesion=self.sesion,
                id_matricula=self.matricula
            ).exists()

            if not existe_asistencia:
                raise ValidationError("No se puede registrar rendimiento sin asistencia")

            posicion = self.matricula.posicion

            actividad_valida = PosicionActividad.objects.filter(
                posicion=posicion,
                actividad=self.actividad
            ).exists()

            if not actividad_valida:
                raise ValidationError("Actividad no válida para la posición")

            atributo_valido = ActividadAtributo.objects.filter(
                actividad=self.actividad,
                atributo=self.atributo
            ).exists()

            if not atributo_valido:
                raise ValidationError("El atributo no corresponde a la actividad")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)