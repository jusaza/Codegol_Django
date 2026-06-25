from datetime import date, time
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from actividad.models import Actividad
from asistencia.models import Asistencia
from atributo.models import Atributo
from atributo_actividad.models import ActividadAtributo
from categoria.models import Categoria
from entrenamientos.models import Entrenamiento
from matricula.models import Matricula
from posicion.models import Posicion
from posicion_actividad.models import PosicionActividad
from rendimiento.models import Rendimiento
from sesion_actividad.models import SesionActividad
from sesion_entrenamiento.models import SesionEntrenamiento
from usuario.models import DetallesUsuarioRol, Rol, Usuario


class RendimientoViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):

        self.rol_entrenador = Rol.objects.create(
            rol_usuario="Entrenador",
            estado=True
        )

        self.posicion = Posicion.objects.create(
            nombre="Delantero"
        )

        self.categoria = Categoria.objects.create(
            nombre_categoria="Sub 15",
            estado=True
        )

        self.entrenador = Usuario.objects.create(
            correo="entrenador@test.com",
            contrasena="Password123!",
            nombre_completo="Carlos Gomez",
            num_identificacion=987654321,
            tipo_documento="cc",
            telefono_1="7654321",
            genero="m",
            fecha_nacimiento=date(1990, 1, 1),
            grupo_sanguineo="a+",
            estado=True
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.entrenador,
            id_rol=self.rol_entrenador
        )

        session = self.client.session
        session["usuario_id"] = self.entrenador.id_usuario
        session["roles"] = ["Entrenador"]
        session.save()

        self.jugador = Usuario.objects.create(
            correo="jugador@test.com",
            contrasena="Password123!",
            nombre_completo="Juan Perez",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="1234567",
            genero="m",
            fecha_nacimiento=date(2010, 1, 1),
            grupo_sanguineo="o+",
            estado=True
        )

        self.otro_jugador = Usuario.objects.create(
            correo="otro@test.com",
            contrasena="Password123!",
            nombre_completo="Pedro Gomez",
            num_identificacion=111222333,
            tipo_documento="cc",
            telefono_1="9998888",
            genero="m",
            fecha_nacimiento=date(2011, 1, 1),
            grupo_sanguineo="b+",
            estado=True
        )

        self.entrenamiento = Entrenamiento.objects.create(
            descripcion="Entrenamiento prueba",
            estado=True,
            lugar="Cancha principal"
        )

        self.actividad = Actividad.objects.create(
            nombre="Calentamiento",
            descripcion="Ejercicio inicial",
            estado=True
        )

        self.atributo = Atributo.objects.create(
            nombre="Velocidad",
            descripcion="Rapidez del jugador"
        )

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad
        )

        ActividadAtributo.objects.create(
            actividad=self.actividad,
            atributo=self.atributo,
            peso=5
        )

        self.sesion = SesionEntrenamiento.objects.create(
            id_entrenamiento=self.entrenamiento,
            id_entrenador=self.entrenador,
            fecha=date(2026, 6, 24),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        self.sesion_anterior = SesionEntrenamiento.objects.create(
            id_entrenamiento=self.entrenamiento,
            id_entrenador=self.entrenador,
            fecha=date(2026, 6, 10),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        SesionActividad.objects.create(
            sesion=self.sesion,
            actividad=self.actividad,
            orden=1,
            duracion_min=15
        )

        SesionActividad.objects.create(
            sesion=self.sesion_anterior,
            actividad=self.actividad,
            orden=1,
            duracion_min=15
        )

        self.matricula = Matricula.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2026, 12, 31),
            nivel="Alto",
            id_jugador=self.jugador,
            posicion=self.posicion,
            estado=True
        )

        self.matricula_otro = Matricula.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2026, 12, 31),
            nivel="Medio",
            id_jugador=self.otro_jugador,
            posicion=self.posicion,
            estado=True
        )

        self.asistencia = Asistencia.objects.create(
            id_sesion=self.sesion,
            id_matricula=self.matricula,
            id_categoria=self.categoria
        )

        Asistencia.objects.create(
            id_sesion=self.sesion_anterior,
            id_matricula=self.matricula,
            id_categoria=self.categoria
        )

        Asistencia.objects.create(
            id_sesion=self.sesion,
            id_matricula=self.matricula_otro,
            id_categoria=self.categoria
        )

        self.rendimiento = Rendimiento.objects.create(
            matricula=self.matricula,
            sesion=self.sesion,
            actividad=self.actividad,
            atributo=self.atributo,
            id_categoria=self.categoria,
            valor=Decimal("7.50")
        )

        Rendimiento.objects.create(
            matricula=self.matricula,
            sesion=self.sesion_anterior,
            actividad=self.actividad,
            atributo=self.atributo,
            id_categoria=self.categoria,
            valor=Decimal("5.00")
        )

        Rendimiento.objects.create(
            matricula=self.matricula_otro,
            sesion=self.sesion,
            actividad=self.actividad,
            atributo=self.atributo,
            id_categoria=self.categoria,
            valor=Decimal("9.00")
        )

    # ==================================================
    # TABLA RENDIMIENTO
    # ==================================================

    def test_tabla_rendimiento_responde_200(self):

        response = self.client.get(
            reverse(
                "tabla_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_tabla_rendimiento_usa_template_correcto(self):

        response = self.client.get(
            reverse(
                "tabla_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertTemplateUsed(
            response,
            "rendimiento/lista.html"
        )

    def test_tabla_rendimiento_envia_contexto(self):

        response = self.client.get(
            reverse(
                "tabla_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertEqual(
            response.context["id_sesion"],
            self.sesion.id_sesion
        )
        self.assertEqual(
            response.context["id_categoria"],
            self.categoria.id_categoria
        )
        self.assertIn(
            self.posicion.nombre,
            response.context["posiciones"]
        )

    def test_tabla_rendimiento_crea_registros(self):

        Rendimiento.objects.all().delete()

        self.client.get(
            reverse(
                "tabla_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertTrue(
            Rendimiento.objects.filter(
                matricula=self.matricula,
                sesion=self.sesion,
                actividad=self.actividad,
                atributo=self.atributo,
                id_categoria=self.categoria
            ).exists()
        )

    def test_tabla_rendimiento_sesion_inexistente(self):

        response = self.client.get(
            reverse(
                "tabla_rendimiento",
                args=[99999, self.categoria.id_categoria]
            )
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # GUARDAR RENDIMIENTO
    # ==================================================

    def test_guardar_rendimiento_post_actualiza_valores(self):

        response = self.client.post(
            reverse(
                "guardar_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            ),
            {
                f"valor_{self.rendimiento.id_rendimiento}": "8,75"
            }
        )

        self.rendimiento.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.rendimiento.valor, Decimal("8.75"))

    def test_guardar_rendimiento_post_limpia_valor_vacio(self):

        response = self.client.post(
            reverse(
                "guardar_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            ),
            {
                f"valor_{self.rendimiento.id_rendimiento}": ""
            }
        )

        self.rendimiento.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.rendimiento.valor)

    def test_guardar_rendimiento_redirecciona_a_lista_sesiones(self):

        response = self.client.post(
            reverse(
                "guardar_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            ),
            {
                f"valor_{self.rendimiento.id_rendimiento}": "6.00"
            }
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_sesiones",
                args=[self.entrenamiento.id_entrenamiento]
            )
        )

    def test_guardar_rendimiento_get_no_modifica_datos(self):

        valor_anterior = self.rendimiento.valor

        self.client.get(
            reverse(
                "guardar_rendimiento",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.rendimiento.refresh_from_db()

        self.assertEqual(self.rendimiento.valor, valor_anterior)

    def test_guardar_rendimiento_sesion_inexistente(self):

        response = self.client.post(
            reverse(
                "guardar_rendimiento",
                args=[99999, self.categoria.id_categoria]
            ),
            {
                f"valor_{self.rendimiento.id_rendimiento}": "7.00"
            }
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # HISTORIAL RENDIMIENTO
    # ==================================================

    def test_historial_rendimiento_responde_200(self):

        response = self.client.get(
            reverse("historial_rendimiento")
        )

        self.assertEqual(response.status_code, 200)

    def test_historial_rendimiento_usa_template_correcto(self):

        response = self.client.get(
            reverse("historial_rendimiento")
        )

        self.assertTemplateUsed(
            response,
            "rendimiento/historial.html"
        )

    def test_historial_rendimiento_muestra_jugadores_con_valores(self):

        response = self.client.get(
            reverse("historial_rendimiento")
        )

        tarjetas = response.context["tarjetas_jugadores"]

        self.assertEqual(len(tarjetas), 2)
        self.assertEqual(
            tarjetas[0]["nombre"],
            self.otro_jugador.nombre_completo
        )
        self.assertEqual(tarjetas[0]["promedio"], 9.0)

    def test_historial_rendimiento_calcula_kpis(self):

        response = self.client.get(
            reverse("historial_rendimiento")
        )

        self.assertEqual(response.context["total_jugadores"], 2)
        self.assertEqual(response.context["promedio_club"], 7.62)
        self.assertEqual(response.context["jugadores_mejorando"], 1)
        self.assertEqual(response.context["jugadores_bajando"], 0)
        self.assertEqual(len(response.context["top_jugadores"]), 2)

    def test_historial_rendimiento_sin_datos(self):

        Rendimiento.objects.all().delete()

        response = self.client.get(
            reverse("historial_rendimiento")
        )

        self.assertEqual(response.context["total_jugadores"], 0)
        self.assertEqual(response.context["promedio_club"], 0)
        self.assertEqual(response.context["top_jugadores"], [])
