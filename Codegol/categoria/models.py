from django.db import models

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)
    estado = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categoria'
        