from rest_framework import serializers
from .models import Product, Supply, Sale


class ProductSerializer(serializers.ModelSerializer):
    """Товар (чтение)."""
    storage_address = serializers.CharField(source="storage.address", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "sku", "price",
            "quantity", "storage", "storage_address",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "quantity", "storage", "storage_address", "created_at", "updated_at")


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление товара. storage берётся из складов компании пользователя."""
    class Meta:
        model = Product
        fields = ("id", "name", "description", "sku", "price", "storage", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_storage(self, value):
        user = self.context["request"].user
        if value.company_id != user.company_id:
            raise serializers.ValidationError("Склад не принадлежит вашей компании.")
        return value


class SupplySerializer(serializers.ModelSerializer):
    """Поставка (чтение)."""
    product_name = serializers.CharField(source="product.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Supply
        fields = (
            "id", "product", "product_name", "supplier", "supplier_name",
            "quantity", "unit_price", "created_by", "created_by_username", "created_at",
        )
        read_only_fields = ("id", "created_by", "created_by_username", "created_at")


class SupplyCreateSerializer(serializers.ModelSerializer):
    """Создание поставки. Увеличивает остаток товара."""
    class Meta:
        model = Supply
        fields = ("id", "product", "supplier", "quantity", "unit_price", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_product(self, value):
        user = self.context["request"].user
        if value.storage.company_id != user.company_id:
            raise serializers.ValidationError("Товар не принадлежит вашей компании.")
        return value

    def validate_supplier(self, value):
        user = self.context["request"].user
        if value.company_id != user.company_id:
            raise serializers.ValidationError("Поставщик не принадлежит вашей компании.")
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        supply = super().create(validated_data)
        # Увеличиваем остаток товара на складе
        product = supply.product
        product.quantity += supply.quantity
        product.save(update_fields=["quantity"])
        return supply


class SaleSerializer(serializers.ModelSerializer):
    """Продажа (чтение)."""
    product_name = serializers.CharField(source="product.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id", "product", "product_name", "quantity", "unit_price",
            "created_by", "created_by_username", "created_at",
        )
        read_only_fields = ("id", "created_by", "created_by_username", "created_at")


class SaleCreateSerializer(serializers.ModelSerializer):
    """Создание продажи. Уменьшает остаток товара."""
    class Meta:
        model = Sale
        fields = ("id", "product", "quantity", "unit_price", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_product(self, value):
        user = self.context["request"].user
        if value.storage.company_id != user.company_id:
            raise serializers.ValidationError("Товар не принадлежит вашей компании.")
        return value

    def validate(self, attrs):
        product = attrs["product"]
        if attrs["quantity"] > product.quantity:
            raise serializers.ValidationError(
                {"quantity": f"Недостаточно товара на складе. Остаток: {product.quantity}."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        sale = super().create(validated_data)
        # Уменьшаем остаток
        product = sale.product
        product.quantity -= sale.quantity
        product.save(update_fields=["quantity"])
        return sale
