from django.db import models
from companies.models import Company
from products.models import Product


class Sale(models.Model):
    """Продажа товаров покупателю."""
    buyer_name = models.CharField("Имя покупателя", max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Компания",
    )
    sale_date = models.DateTimeField("Дата продажи")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        db_table = "sales_sale"
        ordering = ("-sale_date",)

    def __str__(self):
        return f"Продажа #{self.pk} — {self.buyer_name}"

    def delete(self, *args, **kwargs):
        """При удалении продажи возвращаем товары на склад."""
        for item in self.product_sales.select_related("product"):
            item.product.quantity += item.quantity
            item.product.save(update_fields=["quantity"])
        return super().delete(*args, **kwargs)


class ProductSale(models.Model):
    """Промежуточная таблица: товар в продаже с количеством."""
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="product_sales",
        verbose_name="Продажа",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_sales",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "Товар в продаже"
        verbose_name_plural = "Товары в продаже"
        db_table = "sales_product_sale"
        constraints = [
            models.UniqueConstraint(
                fields=["sale", "product"],
                name="unique_sale_product",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"
