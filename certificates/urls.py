from django.urls import path

from .views import (
    GenerationJobView,
    GenerationJobDetailView,
    CertificateDownloadView,
)


urlpatterns = [
    path(
        "jobs/",
        GenerationJobView.as_view(),
        name="generation-job",
    ),
    path(
        "jobs/<int:job_id>/",
        GenerationJobDetailView.as_view(),
        name="generation-job-detail",
    ),
    path(
        "certificates/<int:certificate_id>/",
        CertificateDownloadView.as_view(),
        name="certificate-download",
    ),
]