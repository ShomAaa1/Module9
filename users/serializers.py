from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Регистрация пользователя."""
    # Явно определяем username без model-валидатора — паттерн не попадёт в OpenAPI-схему,
    # но серверная валидация модели (UnicodeUsernameValidator) по-прежнему работает при save().
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "password", "password_confirm",
            "first_name", "last_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        attrs.pop("password_confirm")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя (без пароля)."""
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "is_company_owner", "company", "is_active", "date_joined",
        )
        read_only_fields = fields


class EmployeeSerializer(serializers.ModelSerializer):
    """Сотрудник компании (краткий вид для владельца)."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_company_owner")
        read_only_fields = fields


class AddEmployeeSerializer(serializers.Serializer):
    """Добавление сотрудника в компанию по email."""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        if user.company_id is not None:
            raise serializers.ValidationError("Пользователь уже состоит в компании.")
        if user.is_company_owner:
            raise serializers.ValidationError("Владелец компании не может быть добавлен как сотрудник.")
        return value
