from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "inn", "company", "created_at")
    list_display_links = ("id", "title")
    list_filter = ("company",)
    search_fields = ("title", "inn")
    raw_id_fields = ("company",)
    readonly_fields = ("created_at", "updated_at")
