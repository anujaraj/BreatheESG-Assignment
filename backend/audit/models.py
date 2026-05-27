from django.db import models


class AuditLog(models.Model):
    record = models.ForeignKey(
        "records.NormalizedRecord",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=100)
    previous_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"AuditLog {self.id} on Record {self.record_id}"
