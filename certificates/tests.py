from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import GenerationJob, Certificate
from .services.certificate_generator import generate_certificate


class CertificateAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_generation_job(self):
        """
        Test that a bulk generation job can be created successfully.
        """

        data = {
            "recipients": [
                {
                    "name": "Test User One",
                    "course": "Python Training"
                },
                {
                    "name": "Test User Two",
                    "course": "Django Training"
                }
            ]
        }

        response = self.client.post(
            reverse("generation-job"),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["total_count"],
            2
        )

        self.assertEqual(
            response.data["success_count"],
            2
        )

        self.assertEqual(
            response.data["failure_count"],
            0
        )

        self.assertEqual(
            response.data["status"],
            "COMPLETED"
        )

        self.assertEqual(
            GenerationJob.objects.count(),
            1
        )

        self.assertEqual(
            Certificate.objects.count(),
            2
        )

    def test_input_validation(self):
        """
        Test that invalid recipient data is rejected.
        """

        data = {
            "recipients": [
                {
                    "name": "",
                    "course": "Python Training"
                }
            ]
        }

        response = self.client.post(
            reverse("generation-job"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            GenerationJob.objects.count(),
            0
        )

    @patch("certificates.services.certificate_generator.OUTPUT_DIR")
    def test_certificate_generation(self, mock_output_dir):
        """
        Test that the certificate generator creates a PDF file
        without leaving test files in the real output directory.
        """

        with TemporaryDirectory() as temp_dir:

            mock_output_dir.__truediv__.side_effect = (
                lambda filename: Path(temp_dir) / filename
            )

            file_path = generate_certificate(
                "Test User",
                "Python Training",
                9999
            )

            self.assertTrue(
                Path(file_path).exists()
            )

            self.assertTrue(
                str(file_path).endswith(".pdf")
            )

    def test_job_status(self):
        """
        Test that the job status endpoint returns
        the correct job information.
        """

        data = {
            "recipients": [
                {
                    "name": "Test User",
                    "course": "Python Training"
                }
            ]
        }

        create_response = self.client.post(
            reverse("generation-job"),
            data,
            format="json"
        )

        job_id = create_response.data["job_id"]

        response = self.client.get(
            reverse(
                "generation-job-detail",
                kwargs={"job_id": job_id}
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["job_id"],
            job_id
        )

        self.assertEqual(
            response.data["status"],
            "COMPLETED"
        )

        self.assertEqual(
            response.data["total_count"],
            1
        )

        self.assertEqual(
            response.data["success_count"],
            1
        )

    @patch(
        "certificates.services.job_processor.generate_certificate"
    )
    def test_individual_certificate_failure(
        self,
        mock_generate_certificate
    ):
        """
        Test that failure of one certificate does not
        stop other certificates from being generated.
        """

        def generate_with_failure(
            recipient_name,
            course_name,
            certificate_id
        ):
            if recipient_name == "Fail User":
                raise Exception(
                    "Simulated certificate generation failure"
                )

            return Path(
                f"test_certificate_{certificate_id}.pdf"
            )

        mock_generate_certificate.side_effect = (
            generate_with_failure
        )

        data = {
            "recipients": [
                {
                    "name": "Success User",
                    "course": "Python Training"
                },
                {
                    "name": "Fail User",
                    "course": "Python Training"
                },
                {
                    "name": "Another Success User",
                    "course": "Django Training"
                }
            ]
        }

        response = self.client.post(
            reverse("generation-job"),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["total_count"],
            3
        )

        self.assertEqual(
            response.data["success_count"],
            2
        )

        self.assertEqual(
            response.data["failure_count"],
            1
        )

        self.assertEqual(
            response.data["status"],
            "COMPLETED_WITH_ERRORS"
        )

        job = GenerationJob.objects.get(
            id=response.data["job_id"]
        )

        failed_certificate = job.certificates.get(
            recipient_name="Fail User"
        )

        self.assertEqual(
            failed_certificate.status,
            "FAILED"
        )

        self.assertIn(
            "Simulated certificate generation failure",
            failed_certificate.error_message
        )

    def test_certificate_retrieval(self):
        """
        Test that a successfully generated certificate
        can be retrieved through the API.
        """

        data = {
            "recipients": [
                {
                    "name": "Download User",
                    "course": "Python Training"
                }
            ]
        }

        create_response = self.client.post(
            reverse("generation-job"),
            data,
            format="json"
        )

        job_id = create_response.data["job_id"]

        certificate = Certificate.objects.get(
            job_id=job_id
        )

        response = self.client.get(
            reverse(
                "certificate-download",
                kwargs={
                    "certificate_id": certificate.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf"
        )