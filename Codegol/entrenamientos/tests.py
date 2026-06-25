from django.test import TestCase, Client
from django.urls import reverse

from entrenamientos.models import Entrenamiento
from actividad.models import Actividad
from entrenamiento_actividad.models import EntrenamientoActividad


class PanelEntrenamientoTest(TestCase):

    def setUp(self):

        self.client = Client()

        self.entrenamiento = Entrenamiento.objects.create(
            descripcion="Entrenamiento Inicial",
            lugar="Cancha A",
            observaciones="Observacion de prueba",
            estado=True
        )

        self.actividad = Actividad.objects.create(
            nombre="Control de balón"
        )


    def test_crear_entrenamiento(self):

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "crear_entrenamiento",
                "descripcion": "Entrenamiento físico",
                "lugar": "Cancha Principal",
                "observaciones": "Observaciones válidas"
            }
        )

        self.assertTrue(
            Entrenamiento.objects.filter(
                descripcion="Entrenamiento físico"
            ).exists()
        )


    def test_crear_entrenamiento_descripcion_invalida(self):

        cantidad = Entrenamiento.objects.count()

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "crear_entrenamiento",
                "descripcion": "abc",
                "lugar": "Cancha",
                "observaciones": "Observaciones válidas"
            }
        )

        self.assertEqual(
            Entrenamiento.objects.count(),
            cantidad
        )


    def test_crear_entrenamiento_lugar_invalido(self):

        cantidad = Entrenamiento.objects.count()

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "crear_entrenamiento",
                "descripcion": "Entrenamiento válido",
                "lugar": "A",
                "observaciones": "Observaciones válidas"
            }
        )

        self.assertEqual(
            Entrenamiento.objects.count(),
            cantidad
        )

    def test_crear_entrenamiento_observacion_invalida(self):

        cantidad = Entrenamiento.objects.count()

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "crear_entrenamiento",
                "descripcion": "Entrenamiento válido",
                "lugar": "Cancha",
                "observaciones": "corta"
            }
        )

        self.assertEqual(
            Entrenamiento.objects.count(),
            cantidad
        )


    def test_editar_entrenamiento(self):

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "editar_entrenamiento",
                "id": self.entrenamiento.id_entrenamiento,
                "descripcion": "Entrenamiento Editado",
                "lugar": "Cancha B",
                "observaciones": "Observaciones actualizadas"
            }
        )

        self.entrenamiento.refresh_from_db()

        self.assertEqual(
            self.entrenamiento.descripcion,
            "Entrenamiento Editado"
        )

        self.assertEqual(
            self.entrenamiento.lugar,
            "Cancha B"
        )


    def test_eliminar_entrenamiento(self):

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "eliminar_entrenamiento",
                "id": self.entrenamiento.id_entrenamiento
            }
        )

        self.assertFalse(
            Entrenamiento.objects.filter(
                id_entrenamiento=self.entrenamiento.id_entrenamiento
            ).exists()
        )


    def test_asignar_actividad(self):

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "asignar_actividades",
                "entrenamiento": self.entrenamiento.id_entrenamiento,
                "actividades": [self.actividad.id_actividad],
                f"duracion_{self.actividad.id_actividad}": 20
            }
        )

        self.assertTrue(
            EntrenamientoActividad.objects.filter(
                entrenamiento=self.entrenamiento,
                actividad=self.actividad
            ).exists()
        )


    def test_actualizar_duracion_actividad(self):

        EntrenamientoActividad.objects.create(
            entrenamiento=self.entrenamiento,
            actividad=self.actividad,
            orden=1,
            duracion_min=10
        )

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "asignar_actividades",
                "entrenamiento": self.entrenamiento.id_entrenamiento,
                "actividades": [self.actividad.id_actividad],
                f"duracion_{self.actividad.id_actividad}": 30
            }
        )

        relacion = EntrenamientoActividad.objects.get(
            entrenamiento=self.entrenamiento,
            actividad=self.actividad
        )

        self.assertEqual(
            relacion.duracion_min,
            30
        )


    def test_eliminar_actividad_no_seleccionada(self):

        actividad2 = Actividad.objects.create(
            nombre="Pases"
        )

        EntrenamientoActividad.objects.create(
            entrenamiento=self.entrenamiento,
            actividad=self.actividad,
            orden=1,
            duracion_min=10
        )

        EntrenamientoActividad.objects.create(
            entrenamiento=self.entrenamiento,
            actividad=actividad2,
            orden=2,
            duracion_min=15
        )

        self.client.post(
            reverse("panel_entrenamiento"),
            {
                "tipo": "asignar_actividades",
                "entrenamiento": self.entrenamiento.id_entrenamiento,
                "actividades": [self.actividad.id_actividad],
                f"duracion_{self.actividad.id_actividad}": 10
            }
        )

        self.assertFalse(
            EntrenamientoActividad.objects.filter(
                actividad=actividad2
            ).exists()
        )
