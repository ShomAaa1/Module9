from django.db import models
from companies.models import Company


class Supplier(models.Model):
    """Поставщик, привязанный к компании."""
    title = models.CharField("Название", max_length=255)
    inn = models.CharField("ИНН", max_length=12)
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
        ordering = ("title",)

    def __str__(self):
        return f"{self.title} (ИНН {self.inn})"
