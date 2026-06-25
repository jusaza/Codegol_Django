from django.contrib import admin
from .models import (
    Usuario,
    Rol,
    DetallesUsuarioRol,
    Documentos,
    HistorialDocumentos
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_usuario",
        "nombre_completo",
        "correo",
        "num_identificacion",
        "telefono_1",
        "estado"
    )

    list_filter = (
        "estado",
        "tipo_documento",
        "genero",
        "grupo_sanguineo"
    )

    search_fields = (
        "nombre_completo",
        "correo",
        "num_identificacion"
    )

    ordering = ("nombre_completo",)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = (
        "id_rol",
        "rol_usuario",
        "estado"
    )

    list_filter = ("estado",)
    search_fields = ("rol_usuario",)


@admin.register(DetallesUsuarioRol)
class DetallesUsuarioRolAdmin(admin.ModelAdmin):
    list_display = (
        "id_usuario",
        "id_rol"
    )

    list_filter = ("id_rol",)
    search_fields = (
        "id_usuario__nombre_completo",
        "id_rol__rol_usuario"
    )


@admin.register(Documentos)
class DocumentosAdmin(admin.ModelAdmin):
    list_display = (
        "id_archivo",
        "usuario",
        "tipo_documento",
        "categoria",
        "estado",
        "fecha_subida"
    )

    list_filter = (
        "estado",
        "categoria",
        "tipo_documento"
    )

    search_fields = (
        "nombre",
        "usuario__nombre_completo"
    )

    readonly_fields = (
        "fecha_subida",
    )

    ordering = ("-fecha_subida",)


@admin.register(HistorialDocumentos)
class HistorialDocumentosAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "tipo_documento",
        "nombre",
        "fecha_eliminacion"
    )

    search_fields = (
        "usuario__nombre_completo",
        "nombre",
        "tipo_documento"
    )

    readonly_fields = (
        "fecha_eliminacion",
    )

    ordering = ("-fecha_eliminacion",)
