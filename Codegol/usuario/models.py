from django.db import models

# Create your models here.

from django.db import models

class Usuario(models.Model):

    TIPO_DOCUMENTO = [
        ('cc', 'Cédula de Ciudadanía'),
        ('ti', 'Tarjeta de Identidad'),
        ('ce', 'Cédula de Extranjería'),
        ('pa', 'Pasaporte'),
        ('rc', 'Registro Civil'),
        ('pep', 'Permiso Especial de Permanencia'),
        ('nit', 'NIT'),
        ('nuip', 'NUIP'),
        ('dni', 'DNI'),
        ('ppt', 'Permiso por Protección Temporal'),
    ]

    GENERO = [
        ('m', 'Masculino'),
        ('f', 'Femenino'),
        ('otro', 'Otro'),
    ]

    GRUPO_SANGUINEO_CHOICES = [
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-'),
    ]


    id_usuario = models.AutoField(
        primary_key=True,
    )

    correo = models.EmailField(
        max_length=60,
        unique=True
    )

    contrasena = models.CharField(
        max_length=60
    )

    nombre_completo = models.CharField(
        max_length=60
    )

    num_identificacion = models.PositiveIntegerField(
        unique = True
    )

    tipo_documento = models.CharField(
        max_length=4,
        choices=TIPO_DOCUMENTO
    )

    telefono_1 = models.PositiveBigIntegerField()

    telefono_2 = models.PositiveBigIntegerField(
        null=True,
        blank=True
    )

    direccion = models.CharField(
        max_length=50
    )

    genero = models.CharField(
        max_length=5,
        choices=GENERO
    )

    fecha_nacimiento = models.DateField()

    lugar_nacimiento = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    grupo_sanguineo = models.CharField(
        max_length=3,
        choices=GRUPO_SANGUINEO_CHOICES
    )

    foto_perfil = models.ImageField(
        upload_to='imagenes/',
        verbose_name="imagen de usuario",
        null=True,
        blank=True
    )

    estado = models.BooleanField(
        default=True
    )

    id_usuario_registro = models.ForeignKey(
        'self',  #La tabla de usuario tiene relación con la misma tabla de usuario.
        on_delete=models.PROTECT,
        default=1,
        related_name='usuario_registrado_por'
    )

    id_responsable = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuario_responsable'
    )

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return self.nombre_completo


class Rol(models.Model):

    id_rol = models.AutoField(
        primary_key=True
    )

    estado = models.BooleanField(
        default=True
    )

    rol_usuario = models.CharField(
        max_length=255
    )

    class Meta:
        db_table = "rol"

    def __str__(self):
        return self.rol_usuario
    

class DetallesUsuarioRol(models.Model):

    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario"
    )

    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        db_column="id_rol"
    )

    class Meta:
        db_table = "detalles_usuario_rol"
        unique_together = ("id_usuario", "id_rol")

roles = models.ManyToManyField(
    Rol,
    through='DetallesUsuarioRol'
)
