from django.test import TestCase
from django.urls import reverse

from inventario.models import Inventario


class InventarioViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):
        session = self.client.session
        session["usuario_id"] = 1
        session.save()
        
        self.inventario_1 = Inventario.objects.create(
            nombre_articulo="Balón",
            descripcion="Balón de fútbol",
            estado=True
        )

        self.inventario_2 = Inventario.objects.create(
            nombre_articulo="Conos",
            descripcion="Conos de entrenamiento",
            estado=True
        )

        self.inventario_inactivo = Inventario.objects.create(
            nombre_articulo="Petos",
            descripcion="Petos viejos",
            estado=False
        )

    # ==================================================
    # LISTA ACTIVOS
    # ==================================================

    def test_lista_inventario_carga_correctamente(self):

        response = self.client.get(
            reverse("lista_inventario")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_lista_inventario_muestra_solo_activos(self):

        response = self.client.get(
            reverse("lista_inventario")
        )

        inventarios = response.context["inventarios"]

        self.assertIn(
            self.inventario_1,
            inventarios
        )

        self.assertIn(
            self.inventario_2,
            inventarios
        )

        self.assertNotIn(
            self.inventario_inactivo,
            inventarios
        )

    def test_lista_inventario_filtrar_busqueda(self):

        response = self.client.get(
            reverse("lista_inventario"),
            {
                "q": "Balón"
            }
        )

        inventarios = response.context["inventarios"]

        self.assertEqual(
            len(inventarios),
            1
        )

        self.assertEqual(
            inventarios[0],
            self.inventario_1
        )

    # ==================================================
    # CREAR
    # ==================================================

    def test_crear_inventario_get(self):

        response = self.client.get(
            reverse("crear_inventario")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_crear_inventario_post(self):

        total_antes = Inventario.objects.count()

        response = self.client.post(
            reverse("crear_inventario"),
            {
                "nombre_articulo": "Mallas",
                "descripcion": "Mallas nuevas"
            }
        )

        self.assertEqual(
            Inventario.objects.count(),
            total_antes + 1
        )

        self.assertRedirects(
            response,
            reverse("lista_inventario")
        )

    # ==================================================
    # EDITAR
    # ==================================================

    def test_editar_inventario_get(self):

        response = self.client.get(
            reverse(
                "editar_inventario",
                args=[self.inventario_1.id_inventario]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_editar_inventario_post(self):

        response = self.client.post(
            reverse(
                "editar_inventario",
                args=[self.inventario_1.id_inventario]
            ),
            {
                "nombre_articulo": "Balón Profesional",
                "descripcion": "Actualizado"
            }
        )

        self.inventario_1.refresh_from_db()

        self.assertEqual(
            self.inventario_1.nombre_articulo,
            "Balón Profesional"
        )

        self.assertEqual(
            self.inventario_1.descripcion,
            "Actualizado"
        )

        self.assertRedirects(
            response,
            reverse("lista_inventario")
        )

    def test_editar_inventario_inexistente(self):

        response = self.client.get(
            reverse(
                "editar_inventario",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==================================================
    # ELIMINAR (DESACTIVAR)
    # ==================================================

    def test_eliminar_inventario(self):

        response = self.client.get(
            reverse(
                "eliminar_inventario",
                args=[self.inventario_1.id_inventario]
            )
        )

        self.inventario_1.refresh_from_db()

        self.assertFalse(
            self.inventario_1.estado
        )

        self.assertRedirects(
            response,
            reverse("lista_inventario")
        )

    def test_eliminar_inventario_inexistente(self):

        response = self.client.get(
            reverse(
                "eliminar_inventario",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==================================================
    # INACTIVOS
    # ==================================================

    def test_lista_inventario_inactivos(self):

        response = self.client.get(
            reverse("lista_inventario_inactivos")
        )

        inventarios = response.context["inventarios"]

        self.assertIn(
            self.inventario_inactivo,
            inventarios
        )

        self.assertNotIn(
            self.inventario_1,
            inventarios
        )

    def test_activar_inventario(self):

        response = self.client.get(
            reverse(
                "activar_inventario",
                args=[self.inventario_inactivo.id_inventario]
            )
        )

        self.inventario_inactivo.refresh_from_db()

        self.assertTrue(
            self.inventario_inactivo.estado
        )

        self.assertRedirects(
            response,
            reverse("lista_inventario_inactivos")
        )

    def test_activar_inventario_inexistente(self):

        response = self.client.get(
            reverse(
                "activar_inventario",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )
