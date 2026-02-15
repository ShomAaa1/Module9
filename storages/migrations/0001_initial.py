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
            name="Storage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("address", models.CharField(max_length=512, verbose_name="Адрес")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="storages", to="companies.company", verbose_name="Компания")),
            ],
            options={
                "verbose_name": "Склад",
                "verbose_name_plural": "Склады",
                "db_table": "storages_storage",
            },
        ),
    ]
