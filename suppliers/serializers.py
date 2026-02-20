from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """Поставщик (чтение)."""
    class Meta:
        model = Supplier
        fields = ("id", "title", "inn", "company", "created_at", "updated_at")
        read_only_fields = ("id", "company", "created_at", "updated_at")


class SupplierCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление поставщика. company берётся из user.company."""
    class Meta:
        model = Supplier
        fields = ("id", "title", "inn", "company", "created_at", "updated_at")
        read_only_fields = ("id", "company", "created_at", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.company_id:
            raise serializers.ValidationError("Вы не состоите в компании.")
        validated_data["company"] = user.company
        return super().create(validated_data)
