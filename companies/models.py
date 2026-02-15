from django.db import models


class Company(models.Model):
    """Компания. Владелец определяется через User.is_company_owner."""
    inn = models.CharField("ИНН", max_length=12, unique=True)
    title = models.CharField("Название", max_length=255)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        db_table = "companies_company"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} (ИНН {self.inn})"

    def get_owner(self):
        """Возвращает владельца компании (User с is_company_owner=True)."""
        return self.employees.filter(is_company_owner=True).first()

    def delete(self, *args, **kwargs):
        """При удалении компании сбрасываем is_company_owner и company у всех сотрудников."""
        self.employees.update(is_company_owner=False, company=None)
        return super().delete(*args, **kwargs)
