from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import parsers
from rest_framework.generics import GenericAPIView

import pandas as pd
import io
import numpy as np
import datetime

from organizations.models import Organization
from ingestion.models import DataSource, RawRecord
from records.models import NormalizedRecord
from reviews.models import Review
from audit.models import AuditLog
from .serializers import DataSourceSerializer, RawRecordSerializer, NormalizedRecordSerializer, ReviewSerializer, AuditLogSerializer, UploadSerializer
from .validator import validate_record
from .normalizer import normalize_record


class UploadCSVAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = UploadSerializer

    def post(self, request):
        csv_file = request.FILES.get("file")
        csv_content = request.data.get("content")  # accept raw CSV text in JSON body
        org_name = request.data.get("organization_name")
        source_type = request.data.get("source_type")
        if isinstance(source_type, str):
            source_type = source_type.strip().upper()

        if not (csv_file or csv_content) or not org_name or not source_type:
            return Response({"detail": "file or content, organization_name and source_type are required."}, status=status.HTTP_400_BAD_REQUEST)

        # auto-create or get organization by company_name
        organization, org_created = Organization.objects.get_or_create(company_name=org_name)

        # validate source_type values later, but create a DataSource record first so failures are traceable
        valid_types = [c[0] for c in DataSource.SourceType.choices]

        filename = None
        if csv_file:
            filename = getattr(csv_file, "name", None)
        else:
            filename = request.data.get("filename", "pasted.csv")

        data_source = DataSource.objects.create(
            organization=organization, source_type=source_type, filename=filename
        )

        if source_type not in valid_types:
            data_source.ingestion_status = DataSource.IngestionStatus.FAILED
            data_source.save(update_fields=["ingestion_status"])
            return Response(
                {
                    "detail": "Schema validation failed",
                    "missing_columns": [],
                    "invalid_source_type": source_type,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # transition to PARSING
        data_source.ingestion_status = DataSource.IngestionStatus.PARSING
        data_source.save(update_fields=["ingestion_status"])

        try:
            if csv_content:
                # csv_content is already a str (JSON body)
                text = csv_content
            else:
                raw = csv_file.read()
                try:
                    text = raw.decode("utf-8")
                except Exception:
                    text = raw.decode("latin-1")

            df = pd.read_csv(io.StringIO(text))
        except Exception:
            data_source.ingestion_status = DataSource.IngestionStatus.FAILED
            data_source.save(update_fields=["ingestion_status"])
            return Response(
                {"detail": "Schema validation failed", "missing_columns": []},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def _get_required_columns(source_type):
            return {
                DataSource.SourceType.SAP: [
                    "Document_Number",
                    "Posting_Date",
                    "Plant_Code",
                    "Material_Description",
                    "Quantity",
                    "UOM",
                ],
                DataSource.SourceType.UTILITY: [
                    "Meter_ID",
                    "Billing_Start",
                    "Billing_End",
                    "Consumption",
                    "Unit",
                ],
                DataSource.SourceType.TRAVEL: [
                    "Trip_Type",
                    "Origin",
                    "Destination",
                    "Travel_Date",
                    "Distance",
                ],
            }.get(source_type, [])

        missing_columns = [
            col for col in _get_required_columns(source_type) if col not in df.columns
        ]
        if missing_columns:
            data_source.ingestion_status = DataSource.IngestionStatus.FAILED
            data_source.save(update_fields=["ingestion_status"])
            return Response(
                {"detail": "Schema validation failed", "missing_columns": missing_columns},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def sanitize_for_json(obj):
            if isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [sanitize_for_json(v) for v in obj]

            if obj is None:
                return None

            # pandas / numpy scalars
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)

            # numpy datetime64
            if isinstance(obj, np.datetime64):
                return pd.to_datetime(obj).isoformat()

            # pandas Timestamp or python datetime/date -> ISO string
            if isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
                try:
                    return obj.isoformat()
                except Exception:
                    return str(obj)

            # catch pandas NA / NaN
            try:
                if pd.isna(obj):
                    return None
            except Exception:
                pass

            # numpy generic with .item()
            if hasattr(obj, "item"):
                try:
                    return sanitize_for_json(obj.item())
                except Exception:
                    pass

            return obj

        records = df.to_dict(orient="records")
        raw_records = []
        for row in records:
            rr = RawRecord.objects.create(datasource=data_source, raw_data=sanitize_for_json(row))
            raw_records.append((row, rr))

        # mark parsed
        data_source.ingestion_status = DataSource.IngestionStatus.PARSED
        data_source.save(update_fields=["ingestion_status"])

        validation_summary = {"flagged": False, "severity": "none", "reasons": []}
        row_reviews = []
        for row, raw_record in raw_records:
            validation = validate_record(source_type, row)
            if validation["flagged"]:
                validation_summary["flagged"] = True
                if validation_summary["severity"] != "error":
                    validation_summary["severity"] = validation["severity"]
                validation_summary["reasons"].extend(validation["reasons"])
                row_reviews.append((row, raw_record, validation))

        data_source.ingestion_status = DataSource.IngestionStatus.VALIDATED
        data_source.save(update_fields=["ingestion_status"])

        normalized_ids = []
        for row, raw_record in raw_records:
            normalized_amount, normalized_unit, scope = normalize_record(source_type, row)
            normalized = NormalizedRecord.objects.create(
                raw_record=raw_record,
                scope=scope,
                normalized_amount=normalized_amount,
                normalized_unit=normalized_unit,
                processing_status=NormalizedRecord.ProcessingStatus.COMPLETED,
            )
            normalized_ids.append(normalized.id)
            AuditLog.objects.create(
                record=normalized,
                action="normalized",
                new_values={
                    "scope": scope,
                    "normalized_amount": str(normalized_amount),
                    "normalized_unit": normalized_unit,
                },
            )

            # create review records for flagged rows
            matching = [item for item in row_reviews if item[1].id == raw_record.id]
            if matching:
                _, _, validation = matching[0]
                review = Review.objects.create(
                    record=normalized,
                    flag_reason="; ".join(validation["reasons"]),
                    comments="",
                    approved=False,
                )
                AuditLog.objects.create(
                    record=normalized,
                    action="review_requested",
                    new_values={
                        "review_id": review.id,
                        "flag_reason": review.flag_reason,
                        "approval_status": review.approval_status,
                    },
                )

        data_source.ingestion_status = DataSource.IngestionStatus.NORMALIZED
        data_source.save(update_fields=["ingestion_status"])

        summary = {
            "organization_name": organization.company_name,
            "organization_created": org_created,
            "source_type": source_type,
            "filename": data_source.filename,
            "rows_parsed": len(records),
            "datasource_id": data_source.id,
            "ingestion_status": data_source.ingestion_status,
            "validation": validation_summary,
            "normalized_record_ids": normalized_ids,
        }

        return Response(summary, status=status.HTTP_201_CREATED)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.AllowAny]


class RawRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RawRecord.objects.all()
    serializer_class = RawRecordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        ds = self.request.query_params.get("datasource")
        if ds:
            qs = qs.filter(datasource_id=ds)
        return qs


class NormalizedRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NormalizedRecord.objects.all()
    serializer_class = NormalizedRecordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        raw_record_id = self.request.query_params.get("raw_record")
        if raw_record_id:
            qs = qs.filter(raw_record_id=raw_record_id)
        return qs


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'record__raw_record__datasource'
        )
        status_filter = self.request.query_params.get("approval_status")
        if status_filter:
            qs = qs.filter(approval_status=status_filter)
        return qs

    def _raise_if_locked(self, review):
        if review.approval_status == Review.ApprovalStatus.APPROVED:
            raise PermissionDenied("Approved records are locked for audit.")

    def _sync_normalized_record(self, review):
        normalized = review.record
        normalized.approval_status = review.approval_status
        if review.approval_status == Review.ApprovalStatus.APPROVED:
            normalized.lock_status = normalized.LockStatus.LOCKED
        try:
            normalized.save(update_fields=["approval_status", "lock_status"])
        except ValueError as exc:
            raise PermissionDenied(str(exc))

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        self._raise_if_locked(review)
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        review = serializer.save()
        self._sync_normalized_record(review)
        AuditLog.objects.create(
            record=review.record,
            action="review_{}".format(review.approval_status),
            previous_values={"approved": not review.approved},
            new_values={"approved": review.approved, "approval_status": review.approval_status},
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        review = self.get_object()
        self._raise_if_locked(review)
        review.approved = True
        review.approval_status = Review.ApprovalStatus.APPROVED
        review.save(update_fields=["approved", "approval_status"])
        self._sync_normalized_record(review)
        AuditLog.objects.create(
            record=review.record,
            action="review_approved",
            previous_values={"approved": False, "approval_status": Review.ApprovalStatus.PENDING},
            new_values={"approved": True, "approval_status": review.approval_status},
        )
        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        review = self.get_object()
        self._raise_if_locked(review)
        review.approved = False
        review.approval_status = Review.ApprovalStatus.REJECTED
        review.save(update_fields=["approved", "approval_status"])
        self._sync_normalized_record(review)
        AuditLog.objects.create(
            record=review.record,
            action="review_rejected",
            previous_values={"approved": False, "approval_status": Review.ApprovalStatus.PENDING},
            new_values={"approved": False, "approval_status": review.approval_status},
        )
        return Response(self.get_serializer(review).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-id')
