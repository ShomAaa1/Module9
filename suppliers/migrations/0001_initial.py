# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("inn", models.CharField(max_length=12, verbose_name="ИНН")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="suppliers", to="companies.company", verbose_name="Компания")),
            ],
            options={
                "verbose_name": "Поставщик",
                "verbose_name_plural": "Поставщики",
                "db_table": "suppliers_supplier",
                "ordering": ["title"],
            },
        ),
    ]
