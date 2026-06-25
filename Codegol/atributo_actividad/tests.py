from django.test import TestCase, Client
from django.urls import reverse

from actividad.models import Actividad
from atributo.models import Atributo
from .models import ActividadAtributo


class PanelActividadAtributoTest(TestCase):

    def setUp(self):

        self.client = Client()

        self.actividad = Actividad.objects.create(
            nombre="Control de balón"
        )

        self.atributo = Atributo.objects.create(
            nombre="Velocidad",
            descripcion="Rapidez del jugador"
        )


    def test_crear_atributo(self):

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "atributo",
                "nombre": "Resistencia",
                "descripcion": "Capacidad física"
            }
        )

        self.assertTrue(
            Atributo.objects.filter(
                nombre="Resistencia"
            ).exists()
        )


    def test_asignar_atributo_a_actividad(self):

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "actividad_atributo",
                "actividad": self.actividad.id_actividad,
                "atributos": [self.atributo.id_atributo],
                f"peso_{self.atributo.id_atributo}": 5
            }
        )

        self.assertTrue(
            ActividadAtributo.objects.filter(
                actividad=self.actividad,
                atributo=self.atributo
            ).exists()
        )


    def test_actualizar_peso_atributo(self):

        ActividadAtributo.objects.create(
            actividad=self.actividad,
            atributo=self.atributo,
            peso=2
        )

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "actividad_atributo",
                "actividad": self.actividad.id_actividad,
                "atributos": [self.atributo.id_atributo],
                f"peso_{self.atributo.id_atributo}": 10
            }
        )

        relacion = ActividadAtributo.objects.get(
            actividad=self.actividad,
            atributo=self.atributo
        )

        self.assertEqual(
            relacion.peso,
            10
        )


    def test_eliminar_relacion(self):

        relacion = ActividadAtributo.objects.create(
            actividad=self.actividad,
            atributo=self.atributo,
            peso=5
        )

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "eliminar",
                "id": relacion.id
            }
        )

        self.assertFalse(
            ActividadAtributo.objects.filter(
                id=relacion.id
            ).exists()
        )

    def test_editar_atributo(self):

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "editar_atributo",
                "id": self.atributo.id_atributo,
                "nombre": "Potencia",
                "descripcion": "Fuerza explosiva"
            }
        )

        self.atributo.refresh_from_db()

        self.assertEqual(
            self.atributo.nombre,
            "Potencia"
        )

        self.assertEqual(
            self.atributo.descripcion,
            "Fuerza explosiva"
        )


    def test_eliminar_atributo(self):

        ActividadAtributo.objects.create(
            actividad=self.actividad,
            atributo=self.atributo,
            peso=5
        )

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "eliminar_atributo",
                "id": self.atributo.id_atributo
            }
        )

        self.assertFalse(
            Atributo.objects.filter(
                id_atributo=self.atributo.id_atributo
            ).exists()
        )
   

    def test_eliminar_atributo_y_relaciones(self):

        ActividadAtributo.objects.create(
            actividad=self.actividad,
            atributo=self.atributo,
            peso=3
        )

        self.client.post(
            reverse("panel_actividad_atributo"),
            {
                "tipo": "eliminar_atributo",
                "id": self.atributo.id_atributo
            }
        )

        self.assertEqual(
            ActividadAtributo.objects.count(),
            0
        )
