from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ("id", "record", "flag_reason", "approval_status", "reviewed_at")
	list_filter = ("approval_status",)
	search_fields = ("flag_reason", "comments")
