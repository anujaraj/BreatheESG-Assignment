from django.db import models


class Review(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    record = models.ForeignKey(
        "records.NormalizedRecord",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    flag_reason = models.CharField(max_length=255)
    comments = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            try:
                previous_status = Review.objects.values_list("approval_status", flat=True).get(pk=self.pk)
            except Review.DoesNotExist:
                previous_status = None

        super().save(*args, **kwargs)

        if self.approval_status != previous_status:
            normalized = self.record
            normalized.approval_status = self.approval_status
            if self.approval_status == Review.ApprovalStatus.APPROVED:
                normalized.lock_status = normalized.LockStatus.LOCKED
            normalized.save(update_fields=["approval_status", "lock_status"])

    def __str__(self):
        return f"Review {self.id} for Record {self.record_id}"
