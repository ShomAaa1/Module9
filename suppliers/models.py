from django.db import models
from companies.models import Company


class Supplier(models.Model):
    """Поставщик, привязанный к компании."""
    name = models.CharField("Название", max_length=255)
    contact_info = models.TextField("Контактная информация", blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="suppliers",
        verbose_name="Компания",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        db_table = "suppliers_supplier"
        ordering = ("name",)

    def __str__(self):
        return self.name
