from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contratos", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CampoTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("placeholder", models.CharField(max_length=100)),
                ("label", models.CharField(max_length=255)),
                ("tipo", models.CharField(choices=[("text", "Texto"), ("textarea", "Texto longo"), ("date", "Data"), ("datetime", "Data e hora"), ("number", "Numero"), ("currency", "Moeda"), ("email", "Email"), ("phone", "Telefone"), ("select", "Selecao"), ("multiselect", "Selecao multipla")], default="text", max_length=30)),
                ("obrigatorio", models.BooleanField(default=True)),
                ("mascara", models.CharField(blank=True, max_length=100)),
                ("ajuda", models.CharField(blank=True, max_length=255)),
                ("opcoes", models.JSONField(blank=True, null=True)),
                ("ordem", models.PositiveIntegerField(default=0)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("modelo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="campos", to="contratos.modelocontrato")),
            ],
            options={
                "verbose_name": "Campo de Template",
                "verbose_name_plural": "Campos de Template",
                "ordering": ["ordem", "criado_em"],
                "unique_together": {("modelo", "placeholder")},
            },
        ),
    ]
