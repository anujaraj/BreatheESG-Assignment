from django.db import models


class DataSource(models.Model):
    class SourceType(models.TextChoices):
        SAP = "SAP", "SAP"
        UTILITY = "UTILITY", "Utility"
        TRAVEL = "TRAVEL", "Travel"

    class ProcessingStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    class IngestionStatus(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PARSING = "PARSING", "Parsing"
        PARSED = "PARSED", "Parsed"
        VALIDATED = "VALIDATED", "Validated"
        NORMALIZED = "NORMALIZED", "Normalized"
        FAILED = "FAILED", "Failed"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="data_sources",
    )
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    ingestion_status = models.CharField(
        max_length=20,
        choices=IngestionStatus.choices,
        default=IngestionStatus.UPLOADED,
    )

    class Meta:
        verbose_name = "Data Source"
        verbose_name_plural = "Data Sources"

    def __str__(self):
        return f"{self.organization.company_name} / {self.source_type} / {self.filename}"


class RawRecord(models.Model):
    datasource = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name="raw_records",
    )
    raw_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raw Record"
        verbose_name_plural = "Raw Records"

    def __str__(self):
        return f"RawRecord {self.id} for {self.datasource.filename}"
