from django.db import models


class NormalizedRecord(models.Model):
    """
    Normalized ESG (Environmental, Social, Governance) record.
    
    Converts raw ESG data from multiple sources into standardized format with
    consistent units and scope classification.
    
    SCOPE DEFINITIONS (Greenhouse Gas Protocol):
    - Scope 1: Direct GHG emissions from sources owned/controlled by the organization
      Examples: Fuel combustion in company vehicles, emissions from manufacturing processes
      
    - Scope 2: Indirect GHG emissions from purchased electricity/utilities
      Examples: Electricity purchased from grid for office buildings, steam/heat purchased
      
    - Scope 3: Indirect GHG emissions from other sources (value chain)
      Examples: Business travel, commuting, waste disposal, supply chain emissions
    
    This classification helps organizations track and report their carbon footprint
    across different categories of emissions.
    """
    class Scope(models.TextChoices):
        SCOPE_1 = "Scope 1", "Scope 1 - Direct Emissions"
        SCOPE_2 = "Scope 2", "Scope 2 - Indirect Emissions (Energy)"
        SCOPE_3 = "Scope 3", "Scope 3 - Indirect Emissions (Other)"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class LockStatus(models.TextChoices):
        UNLOCKED = "unlocked", "Unlocked"
        LOCKED = "locked", "Locked"

    class ProcessingStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    raw_record = models.ForeignKey(
        "ingestion.RawRecord",
        on_delete=models.PROTECT,
        related_name="normalized_records",
    )
    scope = models.CharField(max_length=20, choices=Scope.choices)
    normalized_amount = models.DecimalField(max_digits=18, decimal_places=6)
    normalized_unit = models.CharField(max_length=50)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    lock_status = models.CharField(
        max_length=20,
        choices=LockStatus.choices,
        default=LockStatus.UNLOCKED,
    )
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Normalized Record"
        verbose_name_plural = "Normalized Records"

    def _has_modifications(self, current):
        for field in self._meta.fields:
            if field.name in ("id", "created_at"):
                continue
            if getattr(self, field.name) != getattr(current, field.name):
                return True
        return False

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                current = NormalizedRecord.objects.get(pk=self.pk)
            except NormalizedRecord.DoesNotExist:
                current = None
            if (
                current
                and current.approval_status == self.ApprovalStatus.APPROVED
                and current.lock_status == self.LockStatus.LOCKED
                and self._has_modifications(current)
            ):
                raise ValueError("Approved records are locked for audit.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"NormalizedRecord {self.id} ({self.scope})"
