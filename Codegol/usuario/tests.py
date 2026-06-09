from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, DetallesUsuarioRol, Rol, Documentos
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class LoginTest(TestCase):

    def setUp(self):

        self.client = Client()

        self.usuario = Usuario.objects.create(
            nombre_completo="Juan Perez",
            num_identificacion="12345",
            contrasena="123",
            correo="juan@gmail.com"
        )

        self.rol = Rol.objects.create(
            rol_usuario="Administrador"
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.usuario,
            id_rol=self.rol
        )

    def test_login_correcto(self):

        response = self.client.post(
            reverse("login"),
            {
                "documento": "12345",
                "contrasena": "123"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("dashboard")
        )

    def test_login_incorrecto(self):

        response = self.client.post(
            reverse("login"),
            {
                "documento": "12345",
                "contrasena": "999"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("login")
        )


class LogoutTest(TestCase):

    def test_logout(self):

        client = Client()

        session = client.session
        session["usuario_id"] = 1
        session.save()

        response = client.get(
            reverse("logout")
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("login")
        )


class CrearUsuarioTest(TestCase):

    def setUp(self):

        self.client = Client()

        session = self.client.session
        session["roles"] = ["Administrador"]
        session.save()

    def test_crear_usuario(self):

        response = self.client.post(
            reverse("crear_usuario"),
            {
                "nombre_completo": "Pedro Gomez",
                "correo": "pedro@gmail.com",
                "num_identificacion": "99999",
                "contrasena": "123456"
            }
        )

        self.assertTrue(
            Usuario.objects.filter(
                correo="pedro@gmail.com"
            ).exists()
        )


class EliminarUsuarioTest(TestCase):

    def setUp(self):

        self.client = Client()

        session = self.client.session
        session["roles"] = ["Administrador"]
        session.save()

        self.usuario = Usuario.objects.create(
            nombre_completo="Carlos",
            correo="carlos@gmail.com",
            num_identificacion="11111",
            estado=True
        )

    def test_eliminar_usuario(self):

        self.client.get(
            reverse(
                "eliminar_usuario",
                args=[self.usuario.id_usuario]
            )
        )

        self.usuario.refresh_from_db()

        self.assertFalse(
            self.usuario.estado
        )


class ReactivarUsuarioTest(TestCase):

    def setUp(self):

        self.client = Client()

        session = self.client.session
        session["roles"] = ["Administrador"]
        session.save()

        self.usuario = Usuario.objects.create(
            nombre_completo="Carlos",
            correo="carlos@gmail.com",
            num_identificacion="11111",
            estado=False
        )

    def test_reactivar_usuario(self):

        self.client.get(
            reverse(
                "reactivar_usuario",
                args=[self.usuario.id_usuario]
            )
        )

        self.usuario.refresh_from_db()

        self.assertTrue(
            self.usuario.estado
        )


class CambiarEstadoDocumentoTest(TestCase):

    def setUp(self):

        self.client = Client()

        self.usuario = Usuario.objects.create(
            nombre_completo="Juan"
        )

        self.documento = Documentos.objects.create(
            usuario=self.usuario,
            tipo_documento="CC",
            estado="PENDIENTE",
            archivo=SimpleUploadedFile(
                "archivo.pdf",
                b"contenido de prueba"
            )
        )

    def test_aprobar_documento(self):

        self.client.post(
            reverse(
                "cambiar_estado_documento",
                args=[self.documento.id_archivo]
            ),
            {
                "estado": "APROBADO"
            }
        )

        self.documento.refresh_from_db()

        self.assertEqual(
            self.documento.estado,
            "APROBADO"
        )
