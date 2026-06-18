from django.test import TestCase
from django.urls import reverse
from usuario.models import Usuario, Rol, DetallesUsuarioRol
from datetime import date


class UsuarioViewsTest(TestCase):

    def setUp(self):

        self.rol_admin = Rol.objects.create(
            rol_usuario="Administrador"
        )

        self.usuario = Usuario.objects.create(
            correo="admin@test.com",
            contrasena="Admin12345*",
            nombre_completo="Juan Perez",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="3001234567",
            direccion="Calle 123",
            genero="m",
            fecha_nacimiento=date(2000,1,1),
            grupo_sanguineo="o+"
        )

        self.usuario.id_usuario_registro = self.usuario
        self.usuario.save()

        DetallesUsuarioRol.objects.create(
            id_usuario=self.usuario,
            id_rol=self.rol_admin
        )


    def login_admin(self):

        session = self.client.session

        session["usuario_id"] = self.usuario.id_usuario

        session["nombre"] = self.usuario.nombre_completo

        session["roles"] = ["Administrador"]

        session.save()


    def test_login_correcto(self):

        response = self.client.post(

            reverse("login"),

            {

                "documento":123456789,

                "contrasena":"Admin12345*"

            }

        )

        self.assertEqual(response.status_code,302)


    def test_login_incorrecto(self):

        response = self.client.post(

            reverse("login"),

            {

                "documento":123,

                "contrasena":"xxxx"

            }

        )

        self.assertEqual(response.status_code,302)


    def test_logout(self):

        self.login_admin()

        response = self.client.get(

            reverse("logout")

        )

        self.assertEqual(response.status_code,302)


    def test_listar_usuarios(self):

        self.login_admin()

        response = self.client.get(

            reverse("usuario")

        )

        self.assertEqual(response.status_code,200)

        self.assertContains(

            response,

            "Juan Perez"

        )


    def test_eliminar_usuario(self):

        self.login_admin()

        response = self.client.get(

            reverse(

                "eliminar_usuario",

                args=[self.usuario.id_usuario]

            )

        )

        self.usuario.refresh_from_db()

        self.assertFalse(

            self.usuario.estado

        )


    def test_reactivar_usuario(self):

        self.login_admin()

        self.usuario.estado=False

        self.usuario.save()

        response = self.client.get(

            reverse(

                "reactivar_usuario",

                args=[self.usuario.id_usuario]

            )

        )

        self.usuario.refresh_from_db()

        self.assertTrue(

            self.usuario.estado

        )


    def test_ver_documentos(self):

        self.login_admin()

        response = self.client.get(

            reverse(

                "documentos",

                args=[self.usuario.id_usuario]

            )

        )

        self.assertEqual(

            response.status_code,

            200

        )


from unittest.mock import patch


@patch("usuario.views.requests.get")

def test_crear_usuario_get(self,mock_get):

        mock_get.return_value.json.return_value = [

            {

                "alpha2Code":"CO",

                "name":"Colombia"

            }

        ]

        self.login_admin()

        response=self.client.get(

            reverse("crear_usuario")

        )

        self.assertEqual(

            response.status_code,

            200

        )

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from usuario.models import Usuario, Documentos, HistorialDocumentos
from datetime import date


class DocumentoTest(TestCase):

    def setUp(self):

        self.usuario = Usuario.objects.create(
            correo="usuario@test.com",
            contrasena="Admin12345*",
            nombre_completo="Juan Perez",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="3001234567",
            direccion="Calle 123",
            genero="m",
            fecha_nacimiento=date(2000,1,1),
            grupo_sanguineo="o+",
            id_usuario_registro=None
        )

        self.usuario.id_usuario_registro = self.usuario
        self.usuario.save()

        archivo = SimpleUploadedFile(
            "cedula.pdf",
            b"archivo de prueba",
            content_type="application/pdf"
        )

        self.documento = Documentos.objects.create(
            usuario=self.usuario,
            categoria="LEGAL",
            tipo_documento="DNI",
            archivo=archivo,
            nombre="Cedula",
            observaciones="Documento correcto",
            observaciones_rechazo="N.A"
        )


    def test_crear_documento(self):

        self.assertEqual(
            Documentos.objects.count(),
            1
        )

        self.assertEqual(
            self.documento.nombre,
            "Cedula"
        )


    def test_estado_por_defecto(self):

        self.assertEqual(
            self.documento.estado,
            "PENDIENTE"
        )


    def test_aprobar_documento(self):

        self.documento.estado = "APROBADO"

        self.documento.save()

        self.documento.refresh_from_db()

        self.assertEqual(
            self.documento.estado,
            "APROBADO"
        )


    def test_devolver_documento(self):

        self.documento.estado = "DEVUELTO"

        self.documento.observaciones_rechazo = "Documento ilegible"

        self.documento.save()

        self.documento.refresh_from_db()

        self.assertEqual(
            self.documento.estado,
            "DEVUELTO"
        )

        self.assertEqual(
            self.documento.observaciones_rechazo,
            "Documento ilegible"
        )


    def test_eliminar_documento(self):

        self.documento.delete()

        self.assertEqual(
            Documentos.objects.count(),
            0
        )


    def test_historial_documentos(self):

        HistorialDocumentos.objects.create(
            usuario=self.usuario,
            tipo_documento=self.documento.tipo_documento,
            nombre=self.documento.nombre,
            observaciones=self.documento.observaciones,
            observaciones_rechazo=self.documento.observaciones_rechazo
        )

        historial = HistorialDocumentos.objects.first()

        self.assertEqual(
            historial.nombre,
            "Cedula"
        )

        self.assertEqual(
            historial.tipo_documento,
            "DNI"
        )


    def test_relacion_usuario(self):

        self.assertEqual(
            self.documento.usuario,
            self.usuario
        )


    def test_str_documento(self):

        self.assertEqual(
            str(self.documento),
            "Cedula - Juan Perez"
        )
