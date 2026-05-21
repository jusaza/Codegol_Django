from django.test import TestCase
from django.urls import reverse
from .models import Usuario, DetallesUsuarioRol

# Create your tests here.

class UsuarioViewsTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            #Van los objetos o valores para Crear la instacio de Prueba. EJE: nombre = "Julian"
        )
