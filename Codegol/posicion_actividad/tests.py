from django.test import TestCase
from django.urls import reverse

from posicion.models import Posicion
from actividad.models import Actividad
from posicion_actividad.models import PosicionActividad


class PosicionActividadViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):

        session = self.client.session
        session["usuario_id"] = 1
        session.save()

        self.posicion = Posicion.objects.create(
            nombre="Portero"
        )

        self.actividad = Actividad.objects.create(
            nombre="Calentamiento",
            descripcion="Ejercicios previos al entrenamiento",
            estado=True
        )

    # ==================================================
    # PANEL PRINCIPAL
    # ==================================================

    def test_panel_posicion_actividad_get(self):

        response = self.client.get(
            reverse("panel_posicion_actividad")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            self.posicion.nombre
        )

        self.assertContains(
            response,
            self.actividad.nombre
        )

    # ==================================================
    # CREAR POSICION
    # ==================================================

    def test_crear_posicion_correctamente(self):

        total_antes = Posicion.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "posicion",
                "nombre": "Defensa"
            }
        )

        self.assertEqual(
            Posicion.objects.count(),
            total_antes + 1
        )

        self.assertTrue(
            Posicion.objects.filter(
                nombre="Defensa"
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_posicion_nombre_corto(self):

        total_antes = Posicion.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "posicion",
                "nombre": "ABC"
            }
        )

        self.assertEqual(
            Posicion.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_posicion_nombre_largo(self):

        total_antes = Posicion.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "posicion",
                "nombre": "A" * 21
            }
        )

        self.assertEqual(
            Posicion.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_posicion_duplicada(self):

        total_antes = Posicion.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "posicion",
                "nombre": "Portero"
            }
        )

        self.assertEqual(
            Posicion.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    # ==================================================
    # CREAR ACTIVIDAD
    # ==================================================

    def test_crear_actividad_correctamente(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "Pases",
                "descripcion": "Ejercicios de pases largos",
                "estado": "on"
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes + 1
        )

        self.assertTrue(
            Actividad.objects.filter(
                nombre="Pases"
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_actividad_nombre_corto(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "A",
                "descripcion": "Descripcion valida",
                "estado": "on"
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_actividad_nombre_largo(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "A" * 21,
                "descripcion": "Descripcion valida",
                "estado": "on"
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_actividad_descripcion_corta(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "Pases",
                "descripcion": "Muy corta"
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_actividad_descripcion_larga(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "Pases",
                "descripcion": "A" * 61
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_actividad_duplicada(self):

        total_antes = Actividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "actividad",
                "nombre": "Calentamiento",
                "descripcion": "Descripcion valida para probar",
                "estado": "on"
            }
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )
        # ==================================================
    # RELACIONES
    # ==================================================

    def test_crear_relacion_correctamente(self):

        total_antes = PosicionActividad.objects.count()

        response = self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [self.actividad.id_actividad],
                "obligatorio": "on"
            }
        )

        self.assertEqual(
            PosicionActividad.objects.count(),
            total_antes + 1
        )

        relacion = PosicionActividad.objects.get(
            posicion=self.posicion,
            actividad=self.actividad
        )

        self.assertTrue(
            relacion.obligatorio
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_crear_relacion_no_obligatoria(self):

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [self.actividad.id_actividad]
            }
        )

        relacion = PosicionActividad.objects.get(
            posicion=self.posicion,
            actividad=self.actividad
        )

        self.assertFalse(
            relacion.obligatorio
        )

    def test_relacion_no_duplica_registros(self):

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad,
            obligatorio=True
        )

        total_antes = PosicionActividad.objects.count()

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [self.actividad.id_actividad],
                "obligatorio": "on"
            }
        )

        self.assertEqual(
            PosicionActividad.objects.count(),
            total_antes
        )

    def test_relacion_actualiza_obligatorio(self):

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad,
            obligatorio=False
        )

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [self.actividad.id_actividad],
                "obligatorio": "on"
            }
        )

        relacion = PosicionActividad.objects.get(
            posicion=self.posicion,
            actividad=self.actividad
        )

        self.assertTrue(
            relacion.obligatorio
        )

    def test_relacion_elimina_las_que_no_se_envian(self):

        actividad2 = Actividad.objects.create(
            nombre="Remates",
            descripcion="Ejercicios de remates al arco",
            estado=True
        )

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad,
            obligatorio=True
        )

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=actividad2,
            obligatorio=True
        )

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [self.actividad.id_actividad],
                "obligatorio": "on"
            }
        )

        self.assertTrue(
            PosicionActividad.objects.filter(
                actividad=self.actividad
            ).exists()
        )

        self.assertFalse(
            PosicionActividad.objects.filter(
                actividad=actividad2
            ).exists()
        )

    def test_relacion_con_varias_actividades(self):

        actividad2 = Actividad.objects.create(
            nombre="Centros",
            descripcion="Practica de centros al area",
            estado=True
        )

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [
                    self.actividad.id_actividad,
                    actividad2.id_actividad
                ],
                "obligatorio": "on"
            }
        )

        self.assertEqual(
            PosicionActividad.objects.filter(
                posicion=self.posicion
            ).count(),
            2
        )

    def test_relacion_reemplaza_actividades(self):

        actividad2 = Actividad.objects.create(
            nombre="Cabeceo",
            descripcion="Ejercicios de cabeceo ofensivo",
            estado=True
        )

        PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad,
            obligatorio=True
        )

        self.client.post(
            reverse("panel_posicion_actividad"),
            {
                "tipo": "relacion",
                "posicion": self.posicion.id_posicion,
                "actividades": [
                    actividad2.id_actividad
                ],
                "obligatorio": "on"
            }
        )

        self.assertFalse(
            PosicionActividad.objects.filter(
                actividad=self.actividad
            ).exists()
        )

        self.assertTrue(
            PosicionActividad.objects.filter(
                actividad=actividad2
            ).exists()
        )
    
        # ==================================================
    # EDITAR POSICION
    # ==================================================

    def test_editar_posicion_correctamente(self):

        response = self.client.post(
            reverse(
                "editar_posicion",
                args=[self.posicion.id_posicion]
            ),
            {
                "nombre": "Defensa"
            }
        )

        self.posicion.refresh_from_db()

        self.assertEqual(
            self.posicion.nombre,
            "Defensa"
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_editar_posicion_nombre_corto(self):

        nombre_original = self.posicion.nombre

        self.client.post(
            reverse(
                "editar_posicion",
                args=[self.posicion.id_posicion]
            ),
            {
                "nombre": "ABC"
            }
        )

        self.posicion.refresh_from_db()

        self.assertEqual(
            self.posicion.nombre,
            nombre_original
        )

    def test_editar_posicion_duplicada(self):

        Posicion.objects.create(
            nombre="Defensa"
        )

        self.client.post(
            reverse(
                "editar_posicion",
                args=[self.posicion.id_posicion]
            ),
            {
                "nombre": "Defensa"
            }
        )

        self.posicion.refresh_from_db()

        self.assertEqual(
            self.posicion.nombre,
            "Portero"
        )

    # ==================================================
    # EDITAR ACTIVIDAD
    # ==================================================

    def test_editar_actividad_correctamente(self):

        response = self.client.post(
            reverse(
                "editar_actividad",
                args=[self.actividad.id_actividad]
            ),
            {
                "nombre": "Pases",
                "descripcion": "Ejercicios de pases actualizados",
                "estado": "on"
            }
        )

        self.actividad.refresh_from_db()

        self.assertEqual(
            self.actividad.nombre,
            "Pases"
        )

        self.assertEqual(
            self.actividad.descripcion,
            "Ejercicios de pases actualizados"
        )

        self.assertTrue(
            self.actividad.estado
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_editar_actividad_nombre_corto(self):

        nombre_original = self.actividad.nombre

        self.client.post(
            reverse(
                "editar_actividad",
                args=[self.actividad.id_actividad]
            ),
            {
                "nombre": "A",
                "descripcion": "Descripcion suficientemente larga",
                "estado": "on"
            }
        )

        self.actividad.refresh_from_db()

        self.assertEqual(
            self.actividad.nombre,
            nombre_original
        )

    def test_editar_actividad_duplicada(self):

        Actividad.objects.create(
            nombre="Remates",
            descripcion="Ejercicios de remates al arco",
            estado=True
        )

        self.client.post(
            reverse(
                "editar_actividad",
                args=[self.actividad.id_actividad]
            ),
            {
                "nombre": "Remates",
                "descripcion": "Descripcion suficientemente larga",
                "estado": "on"
            }
        )

        self.actividad.refresh_from_db()

        self.assertEqual(
            self.actividad.nombre,
            "Calentamiento"
        )

    # ==================================================
    # ELIMINAR POSICION
    # ==================================================

    def test_eliminar_posicion(self):

        total_antes = Posicion.objects.count()

        response = self.client.get(
            reverse(
                "eliminar_posicion",
                args=[self.posicion.id_posicion]
            )
        )

        self.assertEqual(
            Posicion.objects.count(),
            total_antes - 1
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_eliminar_posicion_inexistente(self):

        response = self.client.get(
            reverse(
                "eliminar_posicion",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==================================================
    # ELIMINAR ACTIVIDAD
    # ==================================================

    def test_eliminar_actividad(self):

        total_antes = Actividad.objects.count()

        response = self.client.get(
            reverse(
                "eliminar_actividad",
                args=[self.actividad.id_actividad]
            )
        )

        self.assertEqual(
            Actividad.objects.count(),
            total_antes - 1
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_eliminar_actividad_inexistente(self):

        response = self.client.get(
            reverse(
                "eliminar_actividad",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # ==================================================
    # ELIMINAR RELACION
    # ==================================================

    def test_eliminar_relacion(self):

        relacion = PosicionActividad.objects.create(
            posicion=self.posicion,
            actividad=self.actividad,
            obligatorio=True
        )

        total_antes = PosicionActividad.objects.count()

        response = self.client.get(
            reverse(
                "eliminar_relacion",
                args=[relacion.id]
            )
        )

        self.assertEqual(
            PosicionActividad.objects.count(),
            total_antes - 1
        )

        self.assertRedirects(
            response,
            reverse("panel_posicion_actividad")
        )

    def test_eliminar_relacion_inexistente(self):

        response = self.client.get(
            reverse(
                "eliminar_relacion",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )