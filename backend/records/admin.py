from django.contrib import admin
from .models import NormalizedRecord


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
	list_display = ("id", "raw_record", "scope", "normalized_amount", "normalized_unit", "processing_status", "approval_status")
	list_filter = ("scope", "processing_status", "approval_status")
	search_fields = ("raw_record__id",)
