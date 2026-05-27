from django.db import models


class Organization(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.company_name
