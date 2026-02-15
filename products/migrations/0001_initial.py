# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("storages", "0001_initial"),
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("sku", models.CharField(blank=True, max_length=100, verbose_name="Артикул")),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="Цена")),
                ("quantity", models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата обновления")),
                ("storage", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="products", to="storages.storage", verbose_name="Склад")),
            ],
            options={
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
                "db_table": "products_product",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Supply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(verbose_name="Количество")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Цена за единицу")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата поставки")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="supplies", to="products.product", verbose_name="Товар")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="supplies", to="suppliers.supplier", verbose_name="Поставщик")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_supplies", to=settings.AUTH_USER_MODEL, verbose_name="Создал")),
            ],
            options={
                "verbose_name": "Поставка",
                "verbose_name_plural": "Поставки",
                "db_table": "products_supply",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Sale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(verbose_name="Количество")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Цена продажи за единицу")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sales", to="products.product", verbose_name="Товар")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_sales", to=settings.AUTH_USER_MODEL, verbose_name="Создал")),
            ],
            options={
                "verbose_name": "Продажа",
                "verbose_name_plural": "Продажи",
                "db_table": "products_sale",
                "ordering": ["-created_at"],
            },
        ),
    ]
