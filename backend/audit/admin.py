from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ("id", "record", "action", "timestamp")
	search_fields = ("action",)
