from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contratos", "0003_campotemplate"),
    ]

    operations = [
        migrations.AddField(
            model_name="contrato",
            name="arquivo_pdf",
            field=models.FileField(blank=True, upload_to="contratos/pdf/"),
        ),
        migrations.AddField(
            model_name="contrato",
            name="supabase_pdf_url",
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]
