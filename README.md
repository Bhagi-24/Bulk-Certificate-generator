# Bulk Certificate Generator API

A Django REST API for generating certificates in bulk from a predefined certificate template.

The API accepts a single request containing multiple recipients, validates the input, creates a generation job, generates individual PDF certificates, tracks the status of each certificate, and provides an API to retrieve generated certificates.

---

## Features

- Bulk certificate generation
- Recipient input validation
- PDF certificate generation using ReportLab
- Database-based job tracking
- Individual certificate status tracking
- Success and failure counts
- Individual certificate failure isolation
- Job status and result API
- Generated certificate download API
- Automated tests
- REST API built using Django REST Framework

---

## Technology Stack

- Python 3.10+
- Django 5.2
- Django REST Framework
- SQLite
- ReportLab
- Git

---

## Project Structure

```text
bulk-certificate-generator/
|
+-- certificates/
|   +-- migrations/
|   +-- services/
|   |   +-- certificate_generator.py
|   |   +-- job_processor.py
|   |
|   +-- models.py
|   +-- serializers.py
|   +-- tests.py
|   +-- urls.py
|   +-- views.py
|
+-- config/
|   +-- settings.py
|   +-- urls.py
|   +-- asgi.py
|   +-- wsgi.py
|
+-- .gitignore
+-- manage.py
+-- requirements.txt
+-- README.md