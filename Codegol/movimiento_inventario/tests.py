from django.test import TestCase
from django.urls import reverse

from usuario.models import Usuario
from inventario.models import Inventario
from movimiento_inventario.models import MovimientoInventario
from entrenamientos.models import Entrenamiento
from sesion_entrenamiento.models import SesionEntrenamiento
from datetime import date

class MovimientoInventarioViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):

        # ------------------------------------------
        # Usuario necesario para las vistas
        # ------------------------------------------

        self.usuario = Usuario.objects.create(
            correo="usuario@test.com",
            contrasena="Password123!",
            nombre_completo="Usuario Prueba",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="3001234567",
            direccion="Calle 1",
            genero="m",
            fecha_nacimiento=date(2000, 1, 1),
            grupo_sanguineo="o+"
        )

        # ------------------------------------------
        # Simular sesión iniciada
        # ------------------------------------------

        session = self.client.session
        session["usuario_id"] = self.usuario.pk

        # Si menu.html utiliza esta variable
        # para marcar la sección activa.
        session["seccion"] = "inventario"

        session.save()

        # ------------------------------------------
        # Inventario de prueba
        # ------------------------------------------

        self.inventario = Inventario.objects.create(
            nombre_articulo="Balón",
            descripcion="Balón profesional",
            estado=True
        )
        # ------------------------------------------
        # Entrenamiento y sesión de prueba
        # ------------------------------------------
        self.entrenamiento = Entrenamiento.objects.create(
            descripcion="Entrenamiento de prueba",
            estado=True,
            lugar="Cancha Principal",
            observaciones="Prueba"
        )

        self.sesion = SesionEntrenamiento.objects.create(
            id_entrenamiento=self.entrenamiento,
            id_entrenador=self.usuario,
            fecha=date.today(),
            hora_inicio="08:00",
            hora_fin="10:00",
            estado=True
        )
        # ------------------------------------------
        # Movimiento entrada
        # ------------------------------------------

        self.entrada = MovimientoInventario.objects.create(
            inventario=self.inventario,
            usuario=self.usuario,
            tipo_movimiento="entrada",
            cantidad=10,
            observaciones="Ingreso inicial"
        )

        # ------------------------------------------
        # Movimiento salida
        # ------------------------------------------

        self.salida = MovimientoInventario.objects.create(
            inventario=self.inventario,
            usuario=self.usuario,
            sesion=self.sesion,
            tipo_movimiento="salida",
            cantidad=3,
            observaciones="Entrenamiento"
        )

        # ------------------------------------------
        # Movimiento devolución
        # ------------------------------------------

        self.devolucion = MovimientoInventario.objects.create(
            inventario=self.inventario,
            usuario=self.usuario,
            sesion=self.sesion,
            tipo_movimiento="devolucion",
            cantidad=1,
            movimiento_padre=self.salida,
            observaciones="Se devolvió parcialmente"
        )


    # ==================================================
    # LISTA DE MOVIMIENTOS
    # ==================================================

    def test_lista_movimientos_carga_correctamente(self):

        response = self.client.get(
            reverse(
                "lista_movimientos",
                args=[self.inventario.id_inventario]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_lista_movimientos_calcula_stock(self):

        response = self.client.get(
            reverse(
                "lista_movimientos",
                args=[self.inventario.id_inventario]
            )
        )

        # 10 entradas - 3 salidas + 1 devolución
        self.assertEqual(
            response.context["stock_total"],
            8
        )


    def test_lista_movimientos_oculta_devoluciones_por_defecto(self):

        response = self.client.get(
            reverse(
                "lista_movimientos",
                args=[self.inventario.id_inventario]
            )
        )

        movimientos = response.context["movimientos"]

        self.assertIn(
            self.entrada,
            movimientos
        )

        self.assertIn(
            self.salida,
            movimientos
        )

        self.assertNotIn(
            self.devolucion,
            movimientos
        )


    def test_lista_movimientos_filtrar_devoluciones(self):

        response = self.client.get(
            reverse(
                "lista_movimientos",
                args=[self.inventario.id_inventario]
            ),
            {
                "q": "devolucion"
            }
        )

        movimientos = response.context["movimientos"]

        self.assertIn(
            self.devolucion,
            movimientos
        )

        self.assertTrue(
            response.context["solo_devoluciones"]
        )


    # ==================================================
    # CREAR MOVIMIENTO
    # ==================================================

    def test_crear_movimiento_get(self):

        response = self.client.get(
            reverse(
                "crear_movimiento",
                args=[self.inventario.id_inventario]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_crear_movimiento_post(self):

        total_antes = MovimientoInventario.objects.count()

        response = self.client.post(
            reverse(
                "crear_movimiento",
                args=[self.inventario.id_inventario]
            ),
            {
                "cantidad": 5,
                "observaciones": "Nueva entrada"
            }
        )

        self.assertEqual(
            MovimientoInventario.objects.count(),
            total_antes + 1
        )

        movimiento = MovimientoInventario.objects.latest("id_movimiento")

        self.assertEqual(
            movimiento.tipo_movimiento,
            "entrada"
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_movimientos",
                args=[self.inventario.id_inventario]
            )
        )


    # ==================================================
    # ACTUALIZAR OBSERVACIONES
    # ==================================================

    def test_actualizar_observaciones(self):

        response = self.client.post(
            reverse("actualizar_observaciones"),
            {
                "ids[]": [self.devolucion.id_movimiento],
                "observaciones[]": ["Observación actualizada"]
            }
        )

        self.devolucion.refresh_from_db()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            self.devolucion.observaciones,
            "Observación actualizada"
        )


    # ==================================================
    # SALIDAS
    # ==================================================

    def test_salidas_sesion_get(self):

        response = self.client.get(
            reverse(
                "salidas_sesion",
                args=[self.sesion.id_sesion]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_salidas_sesion_crear_salida(self):

        total_antes = MovimientoInventario.objects.filter(
            tipo_movimiento="salida"
        ).count()

        response = self.client.post(
            reverse(
                "salidas_sesion",
                args=[self.sesion.id_sesion]
            ),
            {
                "inventario_id": self.inventario.id_inventario,
                "cantidad": 2,
                "observaciones": "Préstamo"
            }
        )

        total_despues = MovimientoInventario.objects.filter(
            tipo_movimiento="salida"
        ).count()

        self.assertEqual(
            total_despues,
            total_antes + 1
        )

        self.assertRedirects(
            response,
            reverse(
                "salidas_sesion",
                args=[self.sesion.id_sesion]
            )
        )


    def test_salidas_sesion_stock_insuficiente(self):

        response = self.client.post(
            reverse(
                "salidas_sesion",
                args=[self.sesion.id_sesion]
            ),
            {
                "inventario_id": self.inventario.id_inventario,
                "cantidad": 100,
                "observaciones": "Prueba"
            }
        )

        self.assertContains(
            response,
            "No hay suficiente stock"
        )


    # ==================================================
    # DEVOLUCIONES
    # ==================================================

    def test_crear_devolucion_get(self):

        response = self.client.get(
            reverse(
                "crear_devolucion",
                args=[self.salida.id_movimiento]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_crear_devolucion_post(self):

        total_antes = MovimientoInventario.objects.filter(
            tipo_movimiento="devolucion"
        ).count()

        response = self.client.post(
            reverse(
                "crear_devolucion",
                args=[self.salida.id_movimiento]
            ),
            {
                "cantidad": 1,
                "observaciones": "Devuelto"
            }
        )

        total_despues = MovimientoInventario.objects.filter(
            tipo_movimiento="devolucion"
        ).count()

        self.assertEqual(
            total_despues,
            total_antes + 1
        )

        self.assertRedirects(
            response,
            reverse(
                "salidas_sesion",
                args=[self.sesion.id_sesion]
            )
        )


    def test_crear_devolucion_excede_prestado(self):

        response = self.client.post(
            reverse(
                "crear_devolucion",
                args=[self.salida.id_movimiento]
            ),
            {
                "cantidad": 10,
                "observaciones": "Prueba"
            }
        )

        self.assertContains(
            response,
            "Excede lo prestado"
        )
