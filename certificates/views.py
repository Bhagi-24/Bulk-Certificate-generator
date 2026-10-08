from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GenerationJob, Certificate
from .serializers import GenerationJobSerializer
from .services.job_processor import process_generation_job
from django.http import FileResponse
from pathlib import Path


class GenerationJobView(APIView):

    def post(self, request):
        serializer = GenerationJobSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipients = serializer.validated_data["recipients"]

        job = GenerationJob.objects.create(
            status="PENDING",
            total_count=len(recipients),
        )

        for recipient in recipients:
            Certificate.objects.create(
                job=job,
                recipient_name=recipient["name"],
                course_name=recipient["course"],
                certificate_date=job.created_at.date(),
                status="PENDING",
            )

        # Process the certificates
        process_generation_job(job)

        return Response(
            {
                "message": "Generation job completed.",
                "job_id": job.id,
                "status": job.status,
                "total_count": job.total_count,
                "success_count": job.success_count,
                "failure_count": job.failure_count,
            },
            status=status.HTTP_201_CREATED,
        )
class GenerationJobDetailView(APIView):

    def get(self, request, job_id):
        try:
            job = GenerationJob.objects.get(id=job_id)
        except GenerationJob.DoesNotExist:
            return Response(
                {
                    "error": "Generation job not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        certificates = []

        for certificate in job.certificates.all():
            certificate_data = {
                "id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "course_name": certificate.course_name,
                "status": certificate.status,
                "error_message": certificate.error_message,
            }

            if certificate.status == "SUCCESS":
                certificate_data["download_url"] = (
                    f"/api/certificates/{certificate.id}/"
                )

            certificates.append(certificate_data)

        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "total_count": job.total_count,
                "success_count": job.success_count,
                "failure_count": job.failure_count,
                "created_at": job.created_at,
                "completed_at": job.completed_at,
                "certificates": certificates,
            },
            status=status.HTTP_200_OK,
        )
class CertificateDownloadView(APIView):

    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(
                id=certificate_id
            )
        except Certificate.DoesNotExist:
            return Response(
                {
                    "error": "Certificate not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if certificate.status != "SUCCESS":
            return Response(
                {
                    "error": "Certificate is not available.",
                    "status": certificate.status,
                    "message": certificate.error_message,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not certificate.file_path:
            return Response(
                {
                    "error": "Certificate file path is missing."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        file_path = Path(certificate.file_path)

        if not file_path.exists():
            return Response(
                {
                    "error": "Certificate file does not exist."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=file_path.name,
            content_type="application/pdf",
        )