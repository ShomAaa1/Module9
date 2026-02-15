from django.db import models
from django.conf import settings
from storages.models import Storage
from suppliers.models import Supplier


class Product(models.Model):
    """Товар, привязанный к складу."""
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    sku = models.CharField("Артикул", max_length=100, blank=True)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Остаток на складе", default=0)
    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Склад",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        db_table = "products_product"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} (остаток: {self.quantity})"


class Supply(models.Model):
    """Поставка товаров от поставщика на склад."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="supplies",
        verbose_name="Товар",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplies",
        verbose_name="Поставщик",
    )
    quantity = models.PositiveIntegerField("Количество")
    unit_price = models.DecimalField("Цена за единицу", max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_supplies",
        verbose_name="Создал",
    )
    created_at = models.DateTimeField("Дата поставки", auto_now_add=True)

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"
        db_table = "products_supply"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Поставка {self.product.name} x{self.quantity} от {self.supplier.name}"


class Sale(models.Model):
    """Продажа товара со склада."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество")
    unit_price = models.DecimalField("Цена продажи за единицу", max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_sales",
        verbose_name="Создал",
    )
    created_at = models.DateTimeField("Дата продажи", auto_now_add=True)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        db_table = "products_sale"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Продажа {self.product.name} x{self.quantity}"
