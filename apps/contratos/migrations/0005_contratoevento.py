from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contratos", "0004_contrato_pdf_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContratoEvento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("acao", models.CharField(max_length=50)),
                ("detalhes", models.CharField(blank=True, max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("contrato", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="eventos", to="contratos.contrato")),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="eventos_contrato", to="core.usuario")),
            ],
            options={
                "verbose_name": "Evento de Contrato",
                "verbose_name_plural": "Eventos de Contrato",
                "ordering": ["-criado_em"],
            },
        ),
    ]
