import io
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from categoria.models import Categoria
from matricula.models import HistorialCategoria, Matricula
from posicion.models import Posicion
from usuario.models import DetallesUsuarioRol, Rol, Usuario


class MatriculaViewsTest(TestCase):

    # ==================================================
    # DATOS INICIALES
    # ==================================================

    def setUp(self):

        self.rol_admin = Rol.objects.create(
            rol_usuario="Administrador",
            estado=True
        )

        self.rol_jugador = Rol.objects.create(
            rol_usuario="Jugador",
            estado=True
        )

        self.posicion = Posicion.objects.create(
            nombre="Delantero"
        )

        self.posicion_portero = Posicion.objects.create(
            nombre="Portero"
        )

        self.categoria = Categoria.objects.create(
            nombre_categoria="Sub 15",
            estado=True
        )

        self.categoria_nueva = Categoria.objects.create(
            nombre_categoria="Sub 17",
            estado=True
        )

        self.admin = Usuario.objects.create(
            correo="admin@test.com",
            contrasena="Password123!",
            nombre_completo="Admin Prueba",
            num_identificacion=111111111,
            tipo_documento="cc",
            telefono_1="3001111111",
            direccion="Calle 1",
            genero="m",
            fecha_nacimiento=date(1990, 1, 1),
            grupo_sanguineo="o+",
            estado=True
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.admin,
            id_rol=self.rol_admin
        )

        self.jugador = Usuario.objects.create(
            correo="jugador@test.com",
            contrasena="Password123!",
            nombre_completo="Juan Perez",
            num_identificacion=222222222,
            tipo_documento="cc",
            telefono_1="3002222222",
            direccion="Calle 2",
            genero="m",
            fecha_nacimiento=date(2000, 1, 1),
            grupo_sanguineo="a+",
            estado=True
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.jugador,
            id_rol=self.rol_jugador
        )

        self.otro_jugador = Usuario.objects.create(
            correo="otro@test.com",
            contrasena="Password123!",
            nombre_completo="Pedro Gomez",
            num_identificacion=333333333,
            tipo_documento="cc",
            telefono_1="3003333333",
            direccion="Calle 3",
            genero="m",
            fecha_nacimiento=date(2001, 1, 1),
            grupo_sanguineo="b+",
            estado=True
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.otro_jugador,
            id_rol=self.rol_jugador
        )

        self.jugador_sin_matricula = Usuario.objects.create(
            correo="nuevo@test.com",
            contrasena="Password123!",
            nombre_completo="Carlos Nuevo",
            num_identificacion=444444444,
            tipo_documento="cc",
            telefono_1="3004444444",
            direccion="Calle 4",
            genero="m",
            fecha_nacimiento=date(2002, 1, 1),
            grupo_sanguineo="ab+",
            estado=True
        )

        DetallesUsuarioRol.objects.create(
            id_usuario=self.jugador_sin_matricula,
            id_rol=self.rol_jugador
        )

        self.matricula_jugador = Matricula.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2026, 12, 31),
            nivel="Alto",
            observaciones="Matricula activa",
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

        self.matricula_inactiva = Matricula.objects.create(
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            nivel="Bajo",
            id_jugador=self.jugador,
            posicion=self.posicion,
            estado=False
        )

        self.historial_jugador = HistorialCategoria.objects.create(
            id_matricula=self.matricula_jugador,
            id_categoria=self.categoria,
            fecha_registro=date(2025, 1, 1),
            estado=True
        )

    def login_admin(self):

        session = self.client.session
        session["usuario_id"] = self.admin.id_usuario
        session["roles"] = ["Administrador"]
        session.save()

    def login_jugador(self):

        session = self.client.session
        session["usuario_id"] = self.jugador.id_usuario
        session["roles"] = ["Jugador"]
        session.save()

    # ==================================================
    # LISTA MATRÍCULA
    # ==================================================

    def test_lista_matricula_responde_200(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula")
        )

        self.assertEqual(response.status_code, 200)

    def test_lista_matricula_usa_template_correcto(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula")
        )

        self.assertTemplateUsed(response, "matricula/lista.html")

    def test_lista_matricula_admin_ve_todas_las_activas(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula")
        )

        matriculas = response.context["matriculas"]

        self.assertEqual(matriculas.count(), 2)
        self.assertFalse(response.context["modo_inactivos"])

    def test_lista_matricula_jugador_solo_ve_las_suyas(self):

        self.login_jugador()

        response = self.client.get(
            reverse("lista_matricula")
        )

        matriculas = response.context["matriculas"]

        self.assertEqual(matriculas.count(), 1)
        self.assertEqual(matriculas.first().id, self.matricula_jugador.id)

    def test_lista_matricula_filtra_por_nombre(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula"),
            {"q": "Pedro"}
        )

        matriculas = response.context["matriculas"]

        self.assertEqual(matriculas.count(), 1)
        self.assertEqual(matriculas.first().id, self.matricula_otro.id)

    def test_lista_matricula_asigna_categoria_actual(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula")
        )

        matriculas = list(response.context["matriculas"])

        matricula = next(
            m for m in matriculas
            if m.id == self.matricula_jugador.id
        )

        self.assertEqual(
            matricula.categoria_actual,
            self.categoria.nombre_categoria
        )

    # ==================================================
    # CREAR MATRÍCULA
    # ==================================================

    def test_crear_matricula_get_muestra_formulario(self):

        self.login_admin()

        response = self.client.get(
            reverse("crear_matricula")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "matricula/form.html")

    def test_crear_matricula_post_crea_registro(self):

        self.login_admin()

        self.client.post(
            reverse("crear_matricula"),
            {
                "fecha_inicio": "2027-01-01",
                "fecha_fin": "2027-12-31",
                "fecha_matricula": "2027-01-01",
                "nivel": "Alto",
                "observaciones": "Nueva matricula",
                "id_jugador": self.jugador_sin_matricula.id_usuario,
                "posicion": self.posicion.id_posicion,
                "categoria": self.categoria.id_categoria
            }
        )

        self.assertTrue(
            Matricula.objects.filter(
                id_jugador=self.jugador_sin_matricula,
                nivel="Alto",
                estado=True
            ).exists()
        )

        matricula = Matricula.objects.get(
            id_jugador=self.jugador_sin_matricula,
            estado=True
        )

        self.assertTrue(
            HistorialCategoria.objects.filter(
                id_matricula=matricula,
                id_categoria=self.categoria,
                estado=True
            ).exists()
        )

    def test_crear_matricula_post_redirecciona_a_lista(self):

        self.login_admin()

        response = self.client.post(
            reverse("crear_matricula"),
            {
                "fecha_inicio": "2027-01-01",
                "fecha_fin": "2027-12-31",
                "fecha_matricula": "2027-01-01",
                "nivel": "Medio",
                "observaciones": "",
                "id_jugador": self.jugador_sin_matricula.id_usuario,
                "posicion": self.posicion.id_posicion,
                "categoria": self.categoria.id_categoria
            }
        )

        self.assertRedirects(response, reverse("lista_matricula"))

    def test_crear_matricula_sin_jugador_muestra_error(self):

        self.login_admin()

        response = self.client.post(
            reverse("crear_matricula"),
            {
                "fecha_inicio": "2027-01-01",
                "fecha_fin": "2027-12-31",
                "nivel": "Alto"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["error"],
            "Debe seleccionar un jugador"
        )

    def test_crear_matricula_fecha_inicio_mayor_muestra_error(self):

        self.login_admin()

        response = self.client.post(
            reverse("crear_matricula"),
            {
                "fecha_inicio": "2028-01-01",
                "fecha_fin": "2027-01-01",
                "nivel": "Alto",
                "id_jugador": self.jugador_sin_matricula.id_usuario,
                "posicion": self.posicion.id_posicion
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "fecha de inicio",
            response.context["error"].lower()
        )

    def test_crear_matricula_solapamiento_muestra_error(self):

        self.login_admin()

        response = self.client.post(
            reverse("crear_matricula"),
            {
                "fecha_inicio": "2025-06-01",
                "fecha_fin": "2026-06-01",
                "nivel": "Alto",
                "id_jugador": self.jugador.id_usuario,
                "posicion": self.posicion.id_posicion
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "matrícula vigente",
            response.context["error"].lower()
        )

    # ==================================================
    # EDITAR MATRÍCULA
    # ==================================================

    def test_editar_matricula_get_muestra_formulario(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "editar_matricula",
                args=[self.matricula_jugador.id]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "matricula/form.html")
        self.assertEqual(
            response.context["matricula"],
            self.matricula_jugador
        )

    def test_editar_matricula_post_actualiza_datos(self):

        self.login_admin()

        response = self.client.post(
            reverse(
                "editar_matricula",
                args=[self.matricula_jugador.id]
            ),
            {
                "fecha_inicio": "2025-02-01",
                "fecha_fin": "2026-11-30",
                "fecha_matricula": "2025-02-01",
                "nivel": "Medio",
                "observaciones": "Actualizada",
                "posicion": self.posicion_portero.id_posicion,
                "categoria": self.categoria.id_categoria
            }
        )

        self.matricula_jugador.refresh_from_db()

        self.assertRedirects(response, reverse("lista_matricula"))
        self.assertEqual(self.matricula_jugador.nivel, "Medio")
        self.assertEqual(
            self.matricula_jugador.observaciones,
            "Actualizada"
        )
        self.assertEqual(
            self.matricula_jugador.posicion_id,
            self.posicion_portero.id_posicion
        )

    def test_editar_matricula_cambia_categoria_crea_historial(self):

        self.login_admin()

        self.client.post(
            reverse(
                "editar_matricula",
                args=[self.matricula_jugador.id]
            ),
            {
                "fecha_inicio": "2025-01-01",
                "fecha_fin": "2026-12-31",
                "fecha_matricula": "2025-01-01",
                "nivel": "Alto",
                "observaciones": "",
                "posicion": self.posicion.id_posicion,
                "categoria": self.categoria_nueva.id_categoria,
                "observacion_categoria": "Ascenso de categoria"
            }
        )

        self.historial_jugador.refresh_from_db()

        self.assertFalse(self.historial_jugador.estado)

        nuevo_historial = HistorialCategoria.objects.get(
            id_matricula=self.matricula_jugador,
            id_categoria=self.categoria_nueva,
            estado=True
        )

        self.assertEqual(
            nuevo_historial.observacion,
            "Ascenso de categoria"
        )

    def test_editar_matricula_inexistente_devuelve_404(self):

        self.login_admin()

        response = self.client.get(
            reverse("editar_matricula", args=[99999])
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # ELIMINAR MATRÍCULA
    # ==================================================

    def test_eliminar_matricula_realiza_borrado_logico(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "eliminar_matricula",
                args=[self.matricula_jugador.id]
            )
        )

        self.matricula_jugador.refresh_from_db()

        self.assertFalse(self.matricula_jugador.estado)
        self.assertRedirects(response, reverse("lista_matricula"))

    def test_eliminar_matricula_inexistente_devuelve_404(self):

        self.login_admin()

        response = self.client.get(
            reverse("eliminar_matricula", args=[99999])
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # ASIGNAR CATEGORÍA
    # ==================================================

    def test_asignar_categoria_post_crea_nuevo_historial(self):

        self.login_admin()

        response = self.client.post(
            reverse(
                "asignar_categoria",
                args=[self.matricula_otro.id]
            ),
            {
                "categoria": self.categoria.id_categoria
            }
        )

        self.assertRedirects(response, reverse("lista_matricula"))

        self.assertTrue(
            HistorialCategoria.objects.filter(
                id_matricula=self.matricula_otro,
                id_categoria=self.categoria,
                estado=True
            ).exists()
        )

    # ==================================================
    # HISTORIAL DE CATEGORÍA
    # ==================================================

    def test_historial_categoria_responde_200(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "historial_categoria",
                args=[self.matricula_jugador.id]
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_historial_categoria_usa_template_correcto(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "historial_categoria",
                args=[self.matricula_jugador.id]
            )
        )

        self.assertTemplateUsed(
            response,
            "matricula/historial_categoria.html"
        )

    def test_historial_categoria_envia_registros(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "historial_categoria",
                args=[self.matricula_jugador.id]
            )
        )

        self.assertEqual(
            len(response.context["historial"]),
            1
        )

    def test_historial_categoria_inexistente_devuelve_404(self):

        self.login_admin()

        response = self.client.get(
            reverse("historial_categoria", args=[99999])
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # CERTIFICADO PDF
    # ==================================================

    def test_certificado_responde_pdf(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "certificado",
                args=[self.matricula_jugador.id]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_certificado_genera_documento_valido(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "certificado",
                args=[self.matricula_jugador.id]
            )
        )

        contenido = response.content

        self.assertTrue(contenido.startswith(b"%PDF"))
        self.assertIn(b"%%EOF", contenido)
        self.assertGreater(len(contenido), 500)

    # ==================================================
    # MODAL FILTRO EXCEL
    # ==================================================

    def test_modal_filtro_excel_responde_200(self):

        self.login_admin()

        response = self.client.get(
            reverse("modal_filtro_excel")
        )

        self.assertEqual(response.status_code, 200)

    def test_modal_filtro_excel_usa_template_correcto(self):

        self.login_admin()

        response = self.client.get(
            reverse("modal_filtro_excel")
        )

        self.assertTemplateUsed(
            response,
            "matricula/modal_filtro_excel.html"
        )

    def test_modal_filtro_excel_envia_categorias_y_posiciones(self):

        self.login_admin()

        response = self.client.get(
            reverse("modal_filtro_excel")
        )

        self.assertIn(self.categoria, response.context["categorias"])
        self.assertIn(self.posicion, response.context["posiciones"])

    # ==================================================
    # EXPORTAR EXCEL
    # ==================================================

    def test_exportar_excel_responde_archivo(self):

        self.login_admin()

        response = self.client.get(
            reverse("exportar_excel")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertIn(
            "reporte_matriculas.xlsx",
            response["Content-Disposition"]
        )

    def test_exportar_excel_filtra_por_nivel(self):

        self.login_admin()

        response = self.client.get(
            reverse("exportar_excel"),
            {"nivel": "Medio"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 100)

    def test_exportar_excel_filtra_por_categoria(self):

        self.login_admin()

        response = self.client.get(
            reverse("exportar_excel"),
            {"categoria": self.categoria.id_categoria}
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 100)

    # ==================================================
    # CARGA MASIVA CSV
    # ==================================================

    def test_carga_masiva_get_muestra_formulario(self):

        self.login_admin()

        response = self.client.get(
            reverse("carga_masiva_matricula")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "matricula/cargar.html")

    def test_carga_masiva_post_sin_archivo_redirecciona(self):

        self.login_admin()

        response = self.client.post(
            reverse("carga_masiva_matricula")
        )

        self.assertRedirects(
            response,
            reverse("carga_masiva_matricula")
        )

    def test_carga_masiva_post_columnas_faltantes_redirecciona(self):

        self.login_admin()

        archivo = SimpleUploadedFile(
            "matriculas.csv",
            b"num_identificacion,fecha_inicio\n222222222,2027-01-01\n",
            content_type="text/csv"
        )

        response = self.client.post(
            reverse("carga_masiva_matricula"),
            {"archivo": archivo}
        )

        self.assertRedirects(
            response,
            reverse("carga_masiva_matricula")
        )

    def test_carga_masiva_post_csv_valido_crea_matricula(self):

        self.login_admin()

        total_antes = Matricula.objects.count()

        contenido = (
            "num_identificacion,fecha_inicio,fecha_fin,nivel,"
            "observaciones,posicion,categoria\n"
            f"{self.jugador_sin_matricula.num_identificacion},"
            "2027-01-01,2027-12-31,Alto,"
            "Importada,Delantero,Sub 15\n"
        )

        archivo = SimpleUploadedFile(
            "matriculas.csv",
            contenido.encode("utf-8"),
            content_type="text/csv"
        )

        response = self.client.post(
            reverse("carga_masiva_matricula"),
            {"archivo": archivo}
        )

        self.assertRedirects(
            response,
            reverse("carga_masiva_matricula")
        )
        self.assertEqual(
            Matricula.objects.count(),
            total_antes + 1
        )

    # ==================================================
    # LISTA INACTIVOS
    # ==================================================

    def test_lista_inactivos_responde_200(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula_inactivos")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "matricula/lista.html")
        self.assertTrue(response.context["modo_inactivos"])

    def test_lista_inactivos_muestra_solo_inactivas(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula_inactivos")
        )

        matriculas = response.context["matriculas"]

        self.assertEqual(matriculas.count(), 1)
        self.assertEqual(
            matriculas.first().id,
            self.matricula_inactiva.id
        )

    def test_lista_inactivos_filtra_por_busqueda(self):

        self.login_admin()

        response = self.client.get(
            reverse("lista_matricula_inactivos"),
            {"q": str(self.matricula_inactiva.id)}
        )

        self.assertEqual(
            response.context["matriculas"].count(),
            1
        )

    # ==================================================
    # ACTIVAR MATRÍCULA
    # ==================================================

    def test_activar_matricula_cambia_estado(self):

        self.login_admin()

        response = self.client.get(
            reverse(
                "activar_matricula",
                args=[self.matricula_inactiva.id]
            )
        )

        self.matricula_inactiva.refresh_from_db()

        self.assertTrue(self.matricula_inactiva.estado)
        self.assertRedirects(
            response,
            reverse("lista_matricula_inactivos")
        )

    def test_activar_matricula_inexistente_devuelve_404(self):

        self.login_admin()

        response = self.client.get(
            reverse("activar_matricula", args=[99999])
        )

        self.assertEqual(response.status_code, 404)
