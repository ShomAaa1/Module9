from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "inn", "title", "get_owner", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("created_at",)
    search_fields = ("inn", "title")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Владелец")
    def get_owner(self, obj):
        owner = obj.get_owner()
        return owner.username if owner else "—"
