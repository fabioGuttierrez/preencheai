from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contratos", "0005_contratoevento"),
    ]

    operations = [
        migrations.AddField(
            model_name="campotemplate",
            name="data_extenso",
            field=models.BooleanField(default=False),
        ),
    ]
