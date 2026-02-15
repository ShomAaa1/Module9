# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("inn", models.CharField(max_length=12, unique=True, verbose_name="ИНН")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
            ],
            options={
                "verbose_name": "Компания",
                "verbose_name_plural": "Компании",
                "db_table": "companies_company",
                "ordering": ["-created_at"],
            },
        ),
    ]
