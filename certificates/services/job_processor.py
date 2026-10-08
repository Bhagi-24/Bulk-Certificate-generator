from django.utils import timezone

from .certificate_generator import generate_certificate
from ..models import GenerationJob


def process_generation_job(job):
    """
    Generate certificates for all recipients in a job.

    Each certificate is processed independently so that
    one failure does not stop the remaining certificates.
    """

    job.status = "PROCESSING"
    job.save(update_fields=["status"])

    success_count = 0
    failure_count = 0

    for certificate in job.certificates.all():

        try:
            file_path = generate_certificate(
                certificate.recipient_name,
                certificate.course_name,
                certificate.id,
            )

            certificate.status = "SUCCESS"
            certificate.file_path = str(file_path)
            certificate.error_message = None
            certificate.save(
                update_fields=[
                    "status",
                    "file_path",
                    "error_message",
                ]
            )

            success_count += 1

        except Exception as error:
            certificate.status = "FAILED"
            certificate.error_message = str(error)
            certificate.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            failure_count += 1

    job.success_count = success_count
    job.failure_count = failure_count

    if failure_count == 0:
        job.status = "COMPLETED"
    elif success_count > 0:
        job.status = "COMPLETED_WITH_ERRORS"
    else:
        job.status = "FAILED"

    job.completed_at = timezone.now()

    job.save(
        update_fields=[
            "success_count",
            "failure_count",
            "status",
            "completed_at",
        ]
    )

    return job