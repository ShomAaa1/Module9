from django.contrib import admin
from .models import Product, Supply, Sale


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sku", "price", "quantity", "storage", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("storage__company",)
    search_fields = ("name", "sku")
    raw_id_fields = ("storage",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "supplier", "quantity", "unit_price", "created_by", "created_at")
    list_display_links = ("id", "product")
    list_filter = ("supplier", "created_at")
    raw_id_fields = ("product", "supplier", "created_by")
    readonly_fields = ("created_at",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity", "unit_price", "created_by", "created_at")
    list_display_links = ("id", "product")
    list_filter = ("created_at",)
    raw_id_fields = ("product", "created_by")
    readonly_fields = ("created_at",)
