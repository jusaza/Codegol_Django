from django.test import TestCase
from django.urls import reverse

from categoria.models import Categoria


class CategoriaViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):
        session = self.client.session
        session['usuario_id'] = 1
        session['roles'] = ['Administrador']
        session['nombre_usuario'] = 'Test'
        session.save()

        self.categoria_1 = Categoria.objects.create(
            nombre_categoria="Sub 10",
            estado=True
        )

        self.categoria_2 = Categoria.objects.create(
            nombre_categoria="Sub 12",
            estado=True
        )

        self.categoria_inactiva = Categoria.objects.create(
            nombre_categoria="Sub 14",
            estado=False
        )

    # ==================================================
    # LISTA
    # ==================================================

    def test_lista_categoria_carga_correctamente(self):
        """
        Debe responder con código 200.
        """

        response = self.client.get(
            reverse("lista_categoria")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_lista_categoria_muestra_solo_activas(self):
        """
        Solo deben mostrarse categorías activas.
        """

        response = self.client.get(
            reverse("lista_categoria")
        )

        categorias = response.context["categorias"]

        self.assertIn(
            self.categoria_1,
            categorias
        )

        self.assertIn(
            self.categoria_2,
            categorias
        )

        self.assertNotIn(
            self.categoria_inactiva,
            categorias
        )

    def test_lista_categoria_filtrar_busqueda(self):
        """
        Debe filtrar correctamente por nombre.
        """

        response = self.client.get(
            reverse("lista_categoria"),
            {
                "q": "Sub 10"
            }
        )

        categorias = response.context["categorias"]

        self.assertEqual(
            categorias.count(),
            1
        )

        self.assertEqual(
            categorias.first(),
            self.categoria_1
        )

    # ==================================================
    # CREAR
    # ==================================================

    def test_crear_categoria_get(self):
        """
        Debe mostrar el formulario.
        """

        response = self.client.get(
            reverse("crear_categoria")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_crear_categoria_post(self):
        """
        Debe crear una categoría nueva.
        """

        total_antes = Categoria.objects.count()

        response = self.client.post(
            reverse("crear_categoria"),
            {
                "nombre_categoria": "Sub 16"
            }
        )

        self.assertEqual(
            Categoria.objects.count(),
            total_antes + 1
        )

        self.assertRedirects(
            response,
            reverse("lista_categoria")
        )

    def test_crear_categoria_nombre_vacio(self):
        """
        No debe crear registros vacíos.
        """

        total_antes = Categoria.objects.count()

        self.client.post(
            reverse("crear_categoria"),
            {
                "nombre_categoria": ""
            }
        )

        self.assertEqual(
            Categoria.objects.count(),
            total_antes
        )

    # ==================================================
    # EDITAR
    # ==================================================

    def test_editar_categoria_get(self):
        """
        Debe cargar el formulario de edición.
        """

        response = self.client.get(
            reverse(
                "editar_categoria",
                args=[self.categoria_1.id_categoria]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_editar_categoria_post(self):
        """
        Debe actualizar el nombre.
        """

        response = self.client.post(
            reverse(
                "editar_categoria",
                args=[self.categoria_1.id_categoria]
            ),
            {
                "nombre_categoria": "Sub 11"
            }
        )

        self.categoria_1.refresh_from_db()

        self.assertEqual(
            self.categoria_1.nombre_categoria,
            "Sub 11"
        )

        self.assertRedirects(
            response,
            reverse("lista_categoria")
        )

    def test_editar_categoria_nombre_vacio(self):
        """
        Si llega vacío no debe modificar.
        """

        nombre_original = (
            self.categoria_1.nombre_categoria
        )

        self.client.post(
            reverse(
                "editar_categoria",
                args=[self.categoria_1.id_categoria]
            ),
            {
                "nombre_categoria": ""
            }
        )

        self.categoria_1.refresh_from_db()

        self.assertEqual(
            self.categoria_1.nombre_categoria,
            nombre_original
        )

    def test_editar_categoria_inexistente(self):
        """
        Debe devolver 404.
        """

        response = self.client.get(
            reverse(
                "editar_categoria",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==================================================
    # ELIMINAR
    # ==================================================

    def test_eliminar_categoria(self):
        """
        Debe realizar borrado lógico.
        """

        response = self.client.get(
            reverse(
                "eliminar_categoria",
                args=[self.categoria_1.id_categoria]
            )
        )

        self.categoria_1.refresh_from_db()

        self.assertFalse(
            self.categoria_1.estado
        )

        self.assertRedirects(
            response,
            reverse("lista_categoria")
        )

    def test_eliminar_categoria_inexistente(self):
        """
        Debe devolver 404.
        """

        response = self.client.get(
            reverse(
                "eliminar_categoria",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )
