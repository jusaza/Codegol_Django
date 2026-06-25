from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse

from usuario.models import (
    Usuario,
    Rol,
    DetallesUsuarioRol
)

from posicion.models import Posicion
from categoria.models import Categoria
from actividad.models import Actividad

from entrenamientos.models import Entrenamiento
from entrenamiento_actividad.models import EntrenamientoActividad

from sesion_entrenamiento.models import SesionEntrenamiento
from sesion_categoria.models import SesionCategoria
from sesion_actividad.models import SesionActividad

from matricula.models import (
    Matricula,
    HistorialCategoria
)

from asistencia.models import Asistencia
from datetime import date, timedelta


class SesionEntrenamientoViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):

        # ------------------------------------------
        # Rol Entrenador
        # ------------------------------------------

        self.rol = Rol.objects.create(
            rol_usuario="Entrenador",
            estado=True
        )

        # ------------------------------------------
        # Usuario Entrenador
        # ------------------------------------------

        self.entrenador = Usuario.objects.create(
            correo="entrenador@test.com",
            contrasena="Password123!",
            nombre_completo="Entrenador Prueba",
            num_identificacion=123456789,
            tipo_documento="cc",
            telefono_1="3001234567",
            direccion="Calle 1",
            genero="m",
            fecha_nacimiento=date(1990, 1, 1),
            grupo_sanguineo="o+"
        )

        # Alias para los tests antiguos
        self.usuario = self.entrenador

        DetallesUsuarioRol.objects.create(
            id_usuario=self.entrenador,
            id_rol=self.rol
        )

        # ------------------------------------------
        # Simular sesión iniciada
        # ------------------------------------------

        session = self.client.session
        session["usuario_id"] = self.entrenador.id_usuario
        session["roles"] = ["Entrenador"]
        session.save()

        # ------------------------------------------
        # Posición
        # ------------------------------------------

        self.posicion = Posicion.objects.create(
            nombre="Delantero"
        )

        # ------------------------------------------
        # Categoría
        # ------------------------------------------

        self.categoria = Categoria.objects.create(
            nombre_categoria="Sub 15",
            estado=True
        )

        # ------------------------------------------
        # Entrenamiento
        # ------------------------------------------

        self.entrenamiento = Entrenamiento.objects.create(
            descripcion="Entrenamiento general",
            estado=True,
            lugar="Cancha Principal",
            observaciones="Ninguna"
        )

        # ------------------------------------------
        # Actividad
        # ------------------------------------------

        self.actividad = Actividad.objects.create(
            nombre="Calentamiento",
            descripcion="Ejercicio inicial",
            estado=True
        )

        self.entrenamiento_actividad = (
            EntrenamientoActividad.objects.create(
                entrenamiento=self.entrenamiento,
                actividad=self.actividad,
                orden=1,
                duracion_min=15
            )
        )

        # ------------------------------------------
        # Sesión
        # ------------------------------------------

        self.sesion = SesionEntrenamiento.objects.create(
            id_entrenamiento=self.entrenamiento,
            id_entrenador=self.entrenador,
            fecha=date.today(),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            estado=True
        )

        # ------------------------------------------
        # Relación sesión-categoría
        # ------------------------------------------

        self.sesion_categoria = SesionCategoria.objects.create(
            id_sesion=self.sesion,
            id_categoria=self.categoria,
            estado=True
        )

        # ------------------------------------------
        # Jugador
        # ------------------------------------------

        self.jugador = Usuario.objects.create(
            correo="jugador@test.com",
            contrasena="Password123!",
            nombre_completo="Jugador Prueba",
            num_identificacion=987654321,
            tipo_documento="cc",
            telefono_1="3007654321",
            direccion="Calle 2",
            genero="m",
            fecha_nacimiento=date(2008, 1, 1),
            grupo_sanguineo="o+"
        )

        # ------------------------------------------
        # Matrícula
        # ------------------------------------------

        self.matricula = Matricula.objects.create(
            estado=True,
            fecha_inicio=date.today() - timedelta(days=10),
            fecha_fin=date.today() + timedelta(days=30),
            nivel="Alto",
            id_jugador=self.jugador,
            posicion=self.posicion
        )

        # ------------------------------------------
        # Historial categoría
        # ------------------------------------------

        self.historial = HistorialCategoria.objects.create(
            id_matricula=self.matricula,
            id_categoria=self.categoria,
            fecha_registro=date.today(),
            estado=True
        )

        # ------------------------------------------
        # Asistencia
        # ------------------------------------------

        self.asistencia = Asistencia.objects.create(
            id_sesion=self.sesion,
            id_matricula=self.matricula,
            id_categoria=self.categoria,
            tipo_asistencia=""
        )
    # ==================================================
    # LISTA SESIONES
    # ==================================================

    def test_lista_sesiones_get(self):

        response = self.client.get(
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_lista_sesiones_contexto(self):

        response = self.client.get(
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )

        self.assertIn(
            self.sesion,
            response.context["sesiones"]
        )

        self.assertIn(
            self.usuario,
            response.context["entrenadores"]
        )

        self.assertIn(
            self.categoria,
            response.context["categorias"]
        )

    def test_lista_sesiones_entrenamiento_inexistente(self):

        response = self.client.get(
            reverse(
                "lista_sesiones",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_lista_sesiones_muestra_categorias(self):

        response = self.client.get(
            reverse(
                "lista_sesiones",
                args=[self.entrenamiento.id_entrenamiento]
            )
        )

        sesion = response.context["sesiones"][0]

        self.assertEqual(
            len(sesion.categorias_registradas),
            1
        )

    def test_lista_sesiones_asistencia_pendiente(self):

        response = self.client.get(
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )

        sesion = response.context["sesiones"][0]

        categoria = sesion.categorias_registradas[0]

        self.assertFalse(
            categoria.asistencia_completa
        )
    from datetime import date, timedelta

    # ==================================================
    # DATOS INICIALES
    # ==================================================


       
        
    # ==================================================
    # CREAR SESIÓN
    # ==================================================

    def test_crear_sesion_get(self):

        response = self.client.get(
            reverse(
                "crear_sesion",
                args=[self.entrenamiento.id_entrenamiento]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            self.categoria.nombre_categoria
        )


    def test_crear_sesion_post(self):

        total_antes = SesionEntrenamiento.objects.count()

        response = self.client.post(
            reverse(
                "crear_sesion",
                args=[self.entrenamiento.id_entrenamiento]
            ),
            {
                "fecha": date.today(),
                "hora_inicio": "08:00",
                "hora_fin": "10:00",
                "categorias[]": [
                    self.categoria.id_categoria
                ]
            }
        )

        self.assertEqual(
            SesionEntrenamiento.objects.count(),
            total_antes + 1
        )

        sesion = SesionEntrenamiento.objects.latest(
            "id_sesion"
        )

        # -----------------------------
        # La sesión quedó creada
        # -----------------------------

        self.assertEqual(
            sesion.id_entrenamiento,
            self.entrenamiento
        )

        self.assertEqual(
            sesion.id_entrenador,
            self.entrenador
        )

        # -----------------------------
        # Se copiaron las actividades
        # -----------------------------

        self.assertTrue(
            SesionActividad.objects.filter(
                sesion=sesion,
                actividad=self.actividad
            ).exists()
        )

        # -----------------------------
        # Se creó la relación sesión-categoría
        # -----------------------------

        self.assertTrue(
            SesionCategoria.objects.filter(
                id_sesion=sesion,
                id_categoria=self.categoria
            ).exists()
        )

        # -----------------------------
        # Se creó la asistencia
        # -----------------------------

        self.assertTrue(
            Asistencia.objects.filter(
                id_sesion=sesion,
                id_categoria=self.categoria,
                id_matricula=self.matricula
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )


    def test_crear_sesion_fecha_pasada(self):

        total_antes = SesionEntrenamiento.objects.count()

        response = self.client.post(
            reverse(
                "crear_sesion",
                args=[self.entrenamiento.id_entrenamiento]
            ),
            {
                "fecha": date.today() - timedelta(days=1),
                "hora_inicio": "08:00",
                "hora_fin": "10:00",
                "categorias[]": [
                    self.categoria.id_categoria
                ]
            },
            follow=True
        )

        self.assertEqual(
            SesionEntrenamiento.objects.count(),
            total_antes
        )

        self.assertContains(
            response,
            "No se pueden crear sesiones"
        )
    # ==================================================
    # EDITAR SESIÓN
    # ==================================================

    def test_editar_sesion_get(self):

        response = self.client.get(
            reverse(
                "editar_sesion",
                args=[self.sesion.id_sesion]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["sesion"],
            self.sesion
        )


    def test_editar_sesion_post(self):

        response = self.client.post(
            reverse(
                "editar_sesion",
                args=[self.sesion.id_sesion]
            ),
            {
                "fecha": date.today() + timedelta(days=2),
                "hora_inicio": "09:00",
                "hora_fin": "11:00",
                "categorias[]": [
                    self.categoria.id_categoria
                ]
            }
        )

        self.sesion.refresh_from_db()

        self.assertEqual(
            self.sesion.hora_inicio.strftime("%H:%M"),
            "09:00"
        )

        self.assertEqual(
            self.sesion.hora_fin.strftime("%H:%M"),
            "11:00"
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )


    def test_editar_sesion_desactiva_categoria_eliminada(self):

        response = self.client.post(
            reverse(
                "editar_sesion",
                args=[self.sesion.id_sesion]
            ),
            {
                "fecha": self.sesion.fecha,
                "hora_inicio": self.sesion.hora_inicio,
                "hora_fin": self.sesion.hora_fin,
                "categorias[]": []
            }
        )

        relacion = SesionCategoria.objects.get(
            id_sesion=self.sesion,
            id_categoria=self.categoria
        )

        self.assertFalse(
            relacion.estado
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )


    def test_editar_sesion_inexistente(self):

        response = self.client.get(
            reverse(
                "editar_sesion",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )
    # ==================================================
    # ELIMINAR SESIÓN
    # ==================================================

    def test_eliminar_sesion(self):

        response = self.client.get(
            reverse(
                "eliminar_sesion",
                args=[self.sesion.id_sesion]
            )
        )

        self.sesion.refresh_from_db()

        self.assertFalse(
            self.sesion.estado
        )

        self.assertRedirects(
            response,
            reverse(
                "lista_sesiones",
                args=[
                    self.entrenamiento.id_entrenamiento
                ]
            )
        )


    def test_eliminar_sesion_inexistente(self):

        response = self.client.get(
            reverse(
                "eliminar_sesion",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )
