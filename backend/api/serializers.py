from rest_framework import serializers

from organizations.models import Organization
from ingestion.models import DataSource, RawRecord
from records.models import NormalizedRecord
from reviews.models import Review
from audit.models import AuditLog


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class DataSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for DataSource objects. Includes nested organization info 
    with both ID and company name for better UI display.
    """
    organization_name = serializers.CharField(source='organization.company_name', read_only=True)
    
    class Meta:
        model = DataSource
        fields = "__all__"


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = "__all__"


class NormalizedRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for NormalizedRecord objects. Includes organization name
    derived from the associated raw record's data source.
    """
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NormalizedRecord
        fields = "__all__"
    
    def get_organization_name(self, obj):
        """Get organization name from the nested relationship chain."""
        try:
            return obj.raw_record.datasource.organization.company_name
        except:
            return None


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review objects. Includes organization name
    for better display in the frontend.
    """
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = "__all__"
    
    def get_organization_name(self, obj):
        """Get organization name from the nested relationship chain."""
        try:
            return obj.record.raw_record.datasource.organization.company_name
        except:
            return None


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    content = serializers.CharField(required=False, allow_blank=True)
    filename = serializers.CharField(required=False)
    organization_name = serializers.CharField(help_text="Company name for onboarding/create-if-missing")
    source_type = serializers.CharField()

    def validate(self, data):
        if not data.get("file") and not data.get("content"):
            raise serializers.ValidationError("Either file or content is required.")
        if not data.get("organization_name"):
            raise serializers.ValidationError("organization_name is required.")
        return data
