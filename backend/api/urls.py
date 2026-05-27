from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadCSVAPIView, DataSourceViewSet, RawRecordViewSet, NormalizedRecordViewSet, ReviewViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r"data-sources", DataSourceViewSet, basename="data-source")
router.register(r"raw-records", RawRecordViewSet, basename="raw-record")
router.register(r"normalized-records", NormalizedRecordViewSet, basename="normalized-record")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("upload/", UploadCSVAPIView.as_view(), name="api-upload-csv"),
    path("", include(router.urls)),
]
