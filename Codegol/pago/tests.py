from datetime import date

from django.test import TestCase
from django.urls import reverse

from matricula.models import Matricula
from pago.models import ConceptoPago, Pago
from posicion.models import Posicion
from usuario.models import DetallesUsuarioRol, Rol, Usuario


class PagoViewsTest(TestCase):

    def setUp(self):
        ConceptoPago.inicializar_conceptos()
        self.concepto_mensualidad = ConceptoPago.objects.get(
            nombre=ConceptoPago.NOMBRE_MENSUALIDAD,
        )
        self.concepto_mensualidad.valor = 150000
        self.concepto_mensualidad.save()

        self.concepto_matricula = ConceptoPago.objects.get(
            nombre=ConceptoPago.NOMBRE_MATRICULA,
        )
        self.concepto_matricula.valor = 200000
        self.concepto_matricula.save()

        self.concepto_uniforme = ConceptoPago.objects.get(
            nombre=ConceptoPago.NOMBRE_UNIFORME,
        )
        self.concepto_uniforme.valor = 80000
        self.concepto_uniforme.save()

        self.concepto_otro = ConceptoPago.objects.get(
            nombre=ConceptoPago.NOMBRE_OTRO,
        )

        self.rol_admin = Rol.objects.create(
            rol_usuario='Administrador',
            estado=True,
        )

        self.rol_jugador = Rol.objects.create(
            rol_usuario='Jugador',
            estado=True,
        )

        self.posicion = Posicion.objects.create(
            nombre='Delantero',
        )

        self.admin = Usuario.objects.create(
            correo='admin@test.com',
            contrasena='Password123!',
            nombre_completo='Admin Prueba',
            num_identificacion=111111111,
            tipo_documento='cc',
            telefono_1='3001111111',
            direccion='Calle 1',
            genero='m',
            fecha_nacimiento=date(1990, 1, 1),
            grupo_sanguineo='o+',
            estado=True,
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.admin,
            id_rol=self.rol_admin,
        )

        self.jugador = Usuario.objects.create(
            correo='jugador@test.com',
            contrasena='Password123!',
            nombre_completo='Juan Perez',
            num_identificacion=222222222,
            tipo_documento='cc',
            telefono_1='3002222222',
            direccion='Calle 2',
            genero='m',
            fecha_nacimiento=date(2010, 1, 1),
            grupo_sanguineo='a+',
            estado=True,
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.jugador,
            id_rol=self.rol_jugador,
        )

        self.otro_jugador = Usuario.objects.create(
            correo='otro@test.com',
            contrasena='Password123!',
            nombre_completo='Pedro Gomez',
            num_identificacion=333333333,
            tipo_documento='cc',
            telefono_1='3003333333',
            direccion='Calle 3',
            genero='m',
            fecha_nacimiento=date(2011, 1, 1),
            grupo_sanguineo='b+',
            estado=True,
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.otro_jugador,
            id_rol=self.rol_jugador,
        )

        self.matricula_jugador = Matricula.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2026, 12, 31),
            nivel='Alto',
            id_jugador=self.jugador,
            posicion=self.posicion,
            estado=True,
        )

        self.matricula_otro = Matricula.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2026, 12, 31),
            nivel='Medio',
            id_jugador=self.otro_jugador,
            posicion=self.posicion,
            estado=True,
        )

        self.pago_jugador = Pago.objects.create(
            id_concepto=self.concepto_mensualidad,
            concepto_pago='Mensualidad enero',
            fecha_pago=date(2026, 1, 15),
            metodo_pago='Efectivo',
            observaciones='Pago al dia',
            valor_total=150000.0,
            cancelado=False,
            id_matricula=self.matricula_jugador,
        )

        self.pago_otro = Pago.objects.create(
            id_concepto=self.concepto_mensualidad,
            concepto_pago='Mensualidad febrero',
            fecha_pago=date(2026, 2, 15),
            metodo_pago='Transferencia',
            observaciones='',
            valor_total=200000.0,
            cancelado=False,
            id_matricula=self.matricula_otro,
        )

    def login_admin(self):
        session = self.client.session
        session['usuario_id'] = self.admin.id_usuario
        session['roles'] = ['Administrador']
        session.save()

    def login_jugador(self):
        session = self.client.session
        session['usuario_id'] = self.jugador.id_usuario
        session['roles'] = ['Jugador']
        session.save()

    def test_lista_pagos_responde_200(self):
        self.login_admin()
        response = self.client.get(reverse('lista_pagos'))
        self.assertEqual(response.status_code, 200)

    def test_lista_pagos_usa_template_correcto(self):
        self.login_admin()
        response = self.client.get(reverse('lista_pagos'))
        self.assertTemplateUsed(response, 'pago/lista.html')

    def test_lista_pagos_admin_ve_todos(self):
        self.login_admin()
        response = self.client.get(reverse('lista_pagos'))
        self.assertEqual(len(response.context['pagos']), 2)

    def test_lista_pagos_jugador_solo_ve_los_suyos(self):
        self.login_jugador()
        response = self.client.get(reverse('lista_pagos'))
        pagos = response.context['pagos']
        self.assertEqual(pagos.count(), 1)
        self.assertEqual(pagos.first().id, self.pago_jugador.id)

    def test_lista_pagos_filtra_por_concepto(self):
        self.login_admin()
        response = self.client.get(reverse('lista_pagos'), {'q': 'enero'})
        self.assertEqual(len(response.context['pagos']), 1)
        self.assertContains(response, 'Mensualidad enero')

    def test_crear_pago_get_muestra_formulario(self):
        self.login_admin()
        response = self.client.get(reverse('crear_pago'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pago/formulario.html')

    def test_crear_pago_mensualidad_usa_valor_del_concepto(self):
        self.login_admin()

        self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_mensualidad.id,
                'fecha_pago': '2026-03-01',
                'metodo_pago': 'Tarjeta',
                'observaciones': 'Pago marzo',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        pago = Pago.objects.get(
            id_matricula=self.matricula_jugador,
            fecha_pago=date(2026, 3, 1),
        )
        self.assertEqual(pago.valor_total, 150000.0)
        self.assertEqual(pago.concepto_pago, 'Mensualidad')

    def test_crear_pago_otro_guarda_nombre_y_valor_personalizados(self):
        self.login_admin()

        self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_otro.id,
                'nombre_otro': 'Balon perdido',
                'valor_otro': '65000',
                'fecha_pago': '2026-03-10',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        pago = Pago.objects.get(concepto_pago='Balon perdido')
        self.assertEqual(pago.valor_total, 65000.0)

    def test_crear_pago_post_redirecciona_a_lista(self):
        self.login_admin()

        response = self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_uniforme.id,
                'fecha_pago': '2026-03-10',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        self.assertRedirects(response, reverse('lista_pagos'))

    def test_no_permite_mensualidad_duplicada_mismo_mes(self):
        self.login_admin()

        response = self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_mensualidad.id,
                'fecha_pago': '2026-01-20',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe una mensualidad registrada')

    def test_no_permite_matricula_duplicada(self):
        self.login_admin()

        Pago.objects.create(
            id_concepto=self.concepto_matricula,
            concepto_pago='Matrícula',
            fecha_pago=date(2026, 1, 1),
            metodo_pago='Efectivo',
            valor_total=200000,
            id_matricula=self.matricula_jugador,
        )

        response = self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_matricula.id,
                'fecha_pago': '2026-02-01',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe un pago de matrícula registrado')

    def test_no_permite_pago_con_matricula_vencida(self):
        self.login_admin()

        matricula_vencida = Matricula.objects.create(
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2025, 6, 30),
            nivel='Bajo',
            id_jugador=self.jugador,
            posicion=self.posicion,
            estado=True,
        )

        response = self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_uniforme.id,
                'fecha_pago': '2026-03-10',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': matricula_vencida.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ha vencido')

    def test_valor_historico_no_cambia_si_concepto_cambia(self):
        self.login_admin()

        self.client.post(
            reverse('crear_pago'),
            {
                'id_concepto': self.concepto_mensualidad.id,
                'fecha_pago': '2026-04-01',
                'metodo_pago': 'Efectivo',
                'observaciones': '',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        pago = Pago.objects.get(fecha_pago=date(2026, 4, 1))
        self.assertEqual(pago.valor_total, 150000.0)

        self.concepto_mensualidad.valor = 999999
        self.concepto_mensualidad.save()

        pago.refresh_from_db()
        self.assertEqual(pago.valor_total, 150000.0)

    def test_editar_pago_get_muestra_formulario(self):
        self.login_admin()
        response = self.client.get(
            reverse('editar_pago', args=[self.pago_jugador.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pago/formulario.html')
        self.assertEqual(response.context['pago'], self.pago_jugador)

    def test_editar_pago_post_actualiza_registro(self):
        self.login_admin()

        response = self.client.post(
            reverse('editar_pago', args=[self.pago_jugador.id]),
            {
                'id_concepto': self.concepto_otro.id,
                'nombre_otro': 'Implemento especial',
                'valor_otro': '45000',
                'fecha_pago': '2026-01-20',
                'metodo_pago': 'Transferencia',
                'observaciones': 'Correccion',
                'id_matricula': self.matricula_jugador.id,
            },
        )

        self.pago_jugador.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.pago_jugador.concepto_pago, 'Implemento especial')
        self.assertEqual(self.pago_jugador.metodo_pago, 'Transferencia')
        self.assertEqual(self.pago_jugador.valor_total, 45000.0)

    def test_cancelar_pago_cambia_estado(self):
        self.login_admin()
        self.assertFalse(self.pago_jugador.cancelado)

        response = self.client.get(
            reverse('cancelar_pago', args=[self.pago_jugador.id]),
        )

        self.pago_jugador.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.pago_jugador.cancelado)

    def test_cancelar_pago_alterna_estado(self):
        self.login_admin()

        self.pago_jugador.cancelado = True
        self.pago_jugador.save()

        self.client.get(
            reverse('cancelar_pago', args=[self.pago_jugador.id]),
        )

        self.pago_jugador.refresh_from_db()
        self.assertFalse(self.pago_jugador.cancelado)

    def test_reporte_pagos_pdf_responde_pdf(self):
        self.login_admin()
        response = self.client.get(reverse('reporte_pagos_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_reporte_pagos_pdf_genera_documento_valido(self):
        self.login_admin()
        response = self.client.get(reverse('reporte_pagos_pdf'))
        contenido = response.content
        self.assertTrue(contenido.startswith(b'%PDF'))
        self.assertIn(b'%%EOF', contenido)
        self.assertGreater(len(contenido), 500)

    def test_actualizar_valores_conceptos(self):
        self.login_admin()

        response = self.client.post(
            reverse('actualizar_valores_conceptos'),
            {
                f'valor_{self.concepto_matricula.id}': '250000',
                f'valor_{self.concepto_mensualidad.id}': '95000',
                f'valor_{self.concepto_uniforme.id}': '70000',
            },
        )

        self.assertRedirects(response, reverse('lista_pagos'))

        self.concepto_matricula.refresh_from_db()
        self.concepto_mensualidad.refresh_from_db()
        self.concepto_uniforme.refresh_from_db()

        self.assertEqual(self.concepto_matricula.valor, 250000)
        self.assertEqual(self.concepto_mensualidad.valor, 95000)
        self.assertEqual(self.concepto_uniforme.valor, 70000)
