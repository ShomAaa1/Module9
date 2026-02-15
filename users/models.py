from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Связь с компанией через FK — несколько пользователей могут принадлежать одной компании.
    """
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        help_text="Буквы, цифры и символы @/./+/-/_",
        validators=[username_validator],
        error_messages={"unique": "Пользователь с таким именем уже существует."},
    )
    email = models.EmailField("Email", unique=True)
    is_company_owner = models.BooleanField("Владелец компании", default=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Компания",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        db_table = "users_user"
