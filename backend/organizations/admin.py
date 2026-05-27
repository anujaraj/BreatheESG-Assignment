from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	list_display = ("id", "company_name", "created_at")
	search_fields = ("company_name",)
