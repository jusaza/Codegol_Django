from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, MaxValueValidator, MinValueValidator

# Create your models here.

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
        validators=[MinLengthValidator(10)],
        max_length=60,
        unique=True,
        blank=False,
        null=False
    )

    password_validator = RegexValidator(
    regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$',
    message='La contraseña debe tener mínimo 10 caracteres, una mayúscula, una minúscula, un número y un carácter especial.'
    )

    contrasena = models.CharField(
        max_length=60,
        validators=[
            MinLengthValidator(10),
            password_validator
        ],
        default="codegol12345",
        blank=False,
        null=False
    )

    nombre_sin_numeros = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$',
    message="El nombre no puede contener números ni caracteres especiales."
    )   

    nombre_completo = models.CharField(
        max_length=30,
        validators=[
            MinLengthValidator(3),
            nombre_sin_numeros
        ],
        blank=False,
        null=False
    )

    num_identificacion = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(100000),      
            MaxValueValidator(9999999999)   
        ],
        blank=False,
        null=False
    )

    tipo_documento = models.CharField(
        max_length=4,
        choices=TIPO_DOCUMENTO,
        blank=False,
        null=False
    )

    telefono_validator = RegexValidator(
    regex=r'^\d{7,10}$',
    message="El teléfono debe tener entre 7 y 10 dígitos."
    )

    telefono_1 = models.CharField(
        max_length=10,
        validators=[telefono_validator]
    )

    telefono_2 = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[telefono_validator]
    )

    direccion = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(4),
        ],
        blank = True
    )

    genero = models.CharField(
        max_length=5,
        choices=GENERO
    )

    fecha_nacimiento = models.DateField()

    lugar_nacimiento = models.CharField(
        max_length=3,
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

    roles = models.ManyToManyField(
        'Rol',
        through='DetallesUsuarioRol'
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
        validators=(
            MinLengthValidator(3),
        ),
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
        db_column="id_usuario",
        related_name="usuario"
    )

    id_rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        db_column="id_rol",
        related_name="rol"
    )

    class Meta:
        db_table = "detalles_usuario_rol"
        unique_together = ("id_usuario", "id_rol")


class Documentos(models.Model):
    CATEGORIA_CHOICES = [
        ('LEGAL', 'Legal'),
        ('MEDICO', 'Médico'),
        ('ACADEMICO', 'Académico'),
        ('DEPORTIVO', 'Deportivo'),
        ('PERSONAL', 'Personal'),
    ]

    ESTADO_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('APROBADO', 'Aprobado'),
    ('DEVUELTO', 'Devuelto'),
    ]

    DOCUMENTACION = [
        ('DNI', 'Documento de Identidad'),
        ('PASAPORTE', 'Pasaporte'),
        ('HOJA_VIDA', 'Hoja de Vida'),
        ('CERT_ANTECEDENTES', 'Certificado de Antecedentes'),
        ('CERT_ESTUDIOS', 'Certificados Académicos'),
        ('LICENCIA_ENTRENADOR', 'Licencia de Entrenador'),
        ('CERT_MEDICO', 'Certificado Médico'),
        ('EPS', 'Certificado EPS'),
        ('ARL', 'Certificado ARL'),
        ('SEGURO', 'Póliza de Seguro'),
        ('FOTO', 'Fotografía'),
        ('AUTORIZACION_PADRES', 'Autorización de Padres'),
        ('REGISTRO_CIVIL', 'Registro Civil'),
        ('CONTRATO', 'Contrato'),
        ('COMPROMISO', 'Carta de Compromiso'),
    ]

    DOCUMENTOS_CATEGORIA_MAP = {
        'DNI': 'LEGAL',
        'PASAPORTE': 'LEGAL',
        'HOJA_VIDA': 'PERSONAL',
        'CERT_ANTECEDENTES': 'LEGAL',
        'CERT_ESTUDIOS': 'ACADEMICO',
        'LICENCIA_ENTRENADOR': 'DEPORTIVO',
        'CERT_MEDICO': 'MEDICO',
        'EPS': 'MEDICO',
        'ARL': 'MEDICO',
        'SEGURO': 'MEDICO',
        'FOTO': 'PERSONAL',
        'AUTORIZACION_PADRES': 'LEGAL',
        'REGISTRO_CIVIL': 'LEGAL',
        'CONTRATO': 'LEGAL',
        'COMPROMISO': 'LEGAL',
    }

    id_archivo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    categoria = models.CharField(
        validators=(
            MinLengthValidator(3),
        ),
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default="SIN_CATEGORIA"
    )
    tipo_documento = models.CharField(
        validators=(
            MinLengthValidator(3),
        ),
        max_length=50,
        choices=DOCUMENTACION
    )
    archivo = models.FileField(upload_to='documentos/')
    nombre = models.CharField(
        validators=(MinLengthValidator(3),
        ),
        max_length=255
        )
    observaciones = models.CharField(max_length=255, 
            default='N.A',
            validators=[MinLengthValidator(3)])
    observaciones_rechazo = models.CharField(
        max_length=255,
        default='N.A',
        validators=[MinLengthValidator(3)])
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    def __str__(self):
        return f"{self.nombre} - {self.usuario}"
    
class HistorialDocumentos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    observaciones_rechazo = models.CharField(max_length=255)
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)
    