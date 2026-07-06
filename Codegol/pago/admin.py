from django.contrib import admin

from .models import ConceptoPago, Pago


@admin.register(ConceptoPago)
class ConceptoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor', 'activo')
    list_editable = ('valor',)
    readonly_fields = ('nombre', 'activo')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'concepto_pago',
        'id_concepto',
        'id_matricula',
        'fecha_pago',
        'metodo_pago',
        'valor_total',
        'cancelado',
    )

    list_filter = (
        'cancelado',
        'metodo_pago',
        'fecha_pago',
        'id_concepto',
    )

    search_fields = (
        'concepto_pago',
        'id_matricula__id_jugador__nombre_completo',
        'id_matricula__id_jugador__num_identificacion',
        'observaciones',
    )

    ordering = ('-fecha_pago',)

    list_editable = ('cancelado',)

    autocomplete_fields = ('id_matricula',)

    readonly_fields = ('valor_total', 'concepto_pago')
