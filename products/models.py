from django.db import models
from django.conf import settings
from storages.models import Storage
from suppliers.models import Supplier


class Product(models.Model):
    """Товар, привязанный к складу. Quantity пополняется только через поставки."""
    title = models.CharField("Название", max_length=255)
    purchase_price = models.DecimalField("Цена закупки", max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField("Цена продажи", max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField("Остаток на складе", default=0)
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
        ordering = ("title",)

    def __str__(self):
        return f"{self.title} (остаток: {self.quantity})"


class Supply(models.Model):
    """Поставка товаров от поставщика. Связь с товарами через SupplyProduct."""
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplies",
        verbose_name="Поставщик",
    )
    delivery_date = models.DateTimeField("Дата поставки", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_supplies",
        verbose_name="Создал",
    )

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"
        db_table = "products_supply"
        ordering = ("-delivery_date",)

    def __str__(self):
        return f"Поставка #{self.pk} от {self.supplier.title}"


class SupplyProduct(models.Model):
    """Промежуточная таблица: товар в поставке с количеством."""
    supply = models.ForeignKey(
        Supply,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Поставка",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="supply_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "Товар в поставке"
        verbose_name_plural = "Товары в поставке"
        db_table = "products_supply_product"

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"
