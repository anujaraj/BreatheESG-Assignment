from django.contrib import admin
from .models import DataSource, RawRecord


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
	list_display = ("id", "organization", "source_type", "filename", "processing_status", "uploaded_at")
	list_filter = ("source_type", "processing_status")


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
	list_display = ("id", "datasource", "created_at")
	search_fields = ("datasource__filename",)
