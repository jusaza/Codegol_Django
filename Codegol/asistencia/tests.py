from django.test import TestCase, Client
from django.urls import reverse

from asistencia.models import Asistencia
from sesion_entrenamiento.models import SesionEntrenamiento
from categoria.models import Categoria
from matricula.models import Matricula, HistorialCategoria
from usuario.models import Usuario
from entrenamientos.models import Entrenamiento
from posicion.models import Posicion


class AsistenciaViewsTest(TestCase):

    # ==================================================
    # CONFIGURACIÓN INICIAL
    # ==================================================
    # Este método se ejecuta antes de cada prueba.
    # Aquí creamos toda la información necesaria para
    # poder probar las vistas.
    # ==================================================

    def setUp(self):

        self.client = Client()

        # --------------------------
        # Usuario jugador
        # --------------------------

        self.usuario = Usuario.objects.create(
            correo="jugador@test.com",
            contrasena="Password123!",
            nombre_completo="Juan Perez",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="1234567",
            genero="m",
            fecha_nacimiento="2010-01-01",
            grupo_sanguineo="o+",
            estado=True
        )

        # --------------------------
        # Posición
        # --------------------------

        self.posicion = Posicion.objects.create(
            nombre="Delantero"
        )

        # --------------------------
        # Matrícula
        # --------------------------

        self.matricula = Matricula.objects.create(
            fecha_inicio="2025-01-01",
            fecha_fin="2026-12-31",
            nivel="Alto",
            id_jugador=self.usuario,
            posicion=self.posicion,
            estado=True
        )

        # --------------------------
        # Categoría
        # --------------------------

        self.categoria = Categoria.objects.create(
            nombre_categoria="Sub 15",
            estado=True
        )

        # --------------------------
        # Entrenamiento
        # --------------------------

        self.entrenamiento = Entrenamiento.objects.create(
            descripcion="Entrenamiento prueba",
            estado=True,
            lugar="Cancha principal"
        )

        # --------------------------
        # Entrenador
        # --------------------------

        self.entrenador = Usuario.objects.create(
            correo="entrenador@test.com",
            contrasena="Password123!",
            nombre_completo="Carlos Gomez",
            num_identificacion=987654321,
            tipo_documento="cc",
            telefono_1="7654321",
            genero="m",
            fecha_nacimiento="1990-01-01",
            grupo_sanguineo="a+",
            estado=True
        )

        # --------------------------
        # Sesión
        # --------------------------

        self.sesion = SesionEntrenamiento.objects.create(
            id_entrenamiento=self.entrenamiento,
            id_entrenador=self.entrenador,
            fecha="2026-06-24",
            hora_inicio="08:00",
            hora_fin="10:00"
        )

        # --------------------------
        # Asistencia
        # --------------------------

        self.asistencia = Asistencia.objects.create(
            id_sesion=self.sesion,
            id_matricula=self.matricula,
            id_categoria=self.categoria
        )

    # ==================================================
    # TABLA ASISTENCIA
    # ==================================================

    def test_tabla_asistencia_responde_200(self):

        """
        Verifica que la vista cargue correctamente.
        """

        response = self.client.get(
            reverse(
                "tabla_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_tabla_asistencia_usa_template_correcto(self):

        """
        Verifica que se utilice el template correcto.
        """

        response = self.client.get(
            reverse(
                "tabla_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertTemplateUsed(
            response,
            "asistencia/lista.html"
        )

    def test_tabla_asistencia_envia_asistencias(self):

        """
        Verifica que la asistencia creada llegue
        al contexto de la plantilla.
        """

        response = self.client.get(
            reverse(
                "tabla_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.assertEqual(
            len(response.context["asistencias"]),
            1
        )

    # ==================================================
    # GUARDAR ASISTENCIA
    # ==================================================

    def test_guardar_asistencia_actualiza_datos(self):

        """
        Verifica que los datos enviados por POST
        se almacenen correctamente.
        """

        response = self.client.post(
            reverse(
                "guardar_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            ),
            {
                f"tipo_{self.asistencia.id_asistencia}":
                    "asiste",

                f"just_{self.asistencia.id_asistencia}":
                    "Llegó puntual",

                f"obs_{self.asistencia.id_asistencia}":
                    "Sin novedades"
            },
            HTTP_REFERER="/asistencia/"
        )

        self.asistencia.refresh_from_db()

        self.assertEqual(
            self.asistencia.tipo_asistencia,
            "asiste"
        )

        self.assertEqual(
            self.asistencia.justificacion,
            "Llegó puntual"
        )

        self.assertEqual(
            self.asistencia.observaciones,
            "Sin novedades"
        )

    def test_guardar_asistencia_redirecciona(self):

        """
        Verifica que al guardar se haga redirect
        a la página anterior.
        """

        response = self.client.post(
            reverse(
                "guardar_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            ),
            HTTP_REFERER="/asistencia/"
        )

        self.assertEqual(
            response.status_code,
            302
        )

    def test_get_no_modifica_asistencia(self):

        """
        Un GET no debe modificar información.
        """

        self.client.get(
            reverse(
                "guardar_asistencia",
                args=[
                    self.sesion.id_sesion,
                    self.categoria.id_categoria
                ]
            )
        )

        self.asistencia.refresh_from_db()

        self.assertEqual(
            self.asistencia.tipo_asistencia,
            ""
        )
