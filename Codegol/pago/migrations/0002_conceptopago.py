# Generated manually for ConceptoPago implementation

import django.db.models.deletion
from django.db import migrations, models


def crear_conceptos_iniciales(apps, schema_editor):
    ConceptoPago = apps.get_model('pago', 'ConceptoPago')
    for nombre in ['Matrícula', 'Mensualidad', 'Uniforme', 'Otro']:
        ConceptoPago.objects.get_or_create(
            nombre=nombre,
            defaults={'valor': 0, 'activo': True},
        )


def asignar_conceptos_a_pagos(apps, schema_editor):
    ConceptoPago = apps.get_model('pago', 'ConceptoPago')
    Pago = apps.get_model('pago', 'Pago')

    conceptos = {c.nombre: c for c in ConceptoPago.objects.all()}
    concepto_otro = conceptos.get('Otro')

    mapeo = {
        'matrícula': conceptos.get('Matrícula'),
        'matricula': conceptos.get('Matrícula'),
        'mensualidad': conceptos.get('Mensualidad'),
        'uniforme': conceptos.get('Uniforme'),
        'uniformes': conceptos.get('Uniforme'),
    }

    for pago in Pago.objects.all():
        nombre = (pago.concepto_pago or '').strip().lower()
        concepto = None

        if nombre in mapeo and mapeo[nombre] is not None:
            concepto = mapeo[nombre]
        elif 'matrícula' in nombre or 'matricula' in nombre:
            concepto = conceptos.get('Matrícula')
        elif 'mensualidad' in nombre:
            concepto = conceptos.get('Mensualidad')
        elif 'uniforme' in nombre:
            concepto = conceptos.get('Uniforme')
        else:
            concepto = concepto_otro

        pago.id_concepto = concepto
        pago.save(update_fields=['id_concepto'])


class Migration(migrations.Migration):

    dependencies = [
        ('pago', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('valor', models.FloatField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Concepto de Pago',
                'verbose_name_plural': 'Conceptos de Pago',
                'ordering': ['id'],
            },
        ),
        migrations.RunPython(crear_conceptos_iniciales, migrations.RunPython.noop),
        migrations.AddField(
            model_name='pago',
            name='id_concepto',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='pagos',
                to='pago.conceptopago',
            ),
        ),
        migrations.RunPython(asignar_conceptos_a_pagos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='pago',
            name='id_concepto',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='pagos',
                to='pago.conceptopago',
            ),
        ),
    ]
