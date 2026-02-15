from django.db import models
from companies.models import Company


class Storage(models.Model):
    """
    Склад компании.
    Сейчас у компании один склад, но в будущем возможно несколько — поэтому ForeignKey.
    Все товары привязываются к конкретному складу.
    """
    address = models.CharField("Адрес", max_length=512)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="storages",
        verbose_name="Компания",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        db_table = "storages_storage"

    def __str__(self):
        return f"Склад «{self.company.title}» — {self.address}"
