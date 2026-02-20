from django.contrib import admin
from .models import Product, Supply, SupplyProduct


class SupplyProductInline(admin.TabularInline):
    model = SupplyProduct
    extra = 1
    raw_id_fields = ("product",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "purchase_price", "sale_price", "quantity", "storage", "created_at")
    list_display_links = ("id", "title")
    list_filter = ("storage__company",)
    search_fields = ("title",)
    raw_id_fields = ("storage",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "delivery_date", "created_by")
    list_display_links = ("id", "supplier")
    list_filter = ("supplier", "delivery_date")
    raw_id_fields = ("supplier", "created_by")
    readonly_fields = ("delivery_date",)
    inlines = (SupplyProductInline,)


@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ("id", "supply", "product", "quantity")
    list_display_links = ("id",)
    raw_id_fields = ("supply", "product")
