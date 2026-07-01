from django.db import models

# Create your models here.

class SesionEntrenamiento(models.Model):
    id_sesion = models.AutoField(primary_key=True)
    id_entrenamiento = models.ForeignKey(
        'entrenamientos.Entrenamiento',  
        on_delete=models.CASCADE
    )
    id_entrenador = models.ForeignKey(
        'usuario.Usuario',
        on_delete=models.CASCADE
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.BooleanField(default=True)  # 👈 para borrado lógico

    class Meta:
        db_table = 'sesion_entrenamiento'

    def __str__(self):
        return f"Sesión {self.id_sesion} - {self.fecha}"
    