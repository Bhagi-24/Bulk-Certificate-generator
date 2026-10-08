from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "generated_certificates"

OUTPUT_DIR.mkdir(exist_ok=True)


def generate_certificate(
    recipient_name,
    course_name,
    certificate_id,
    certificate_date=None,
):
    """
    Generate a professional certificate PDF for one recipient.

    Args:
        recipient_name: Name of the certificate recipient.
        course_name: Name of the completed course.
        certificate_id: Database ID of the certificate.
        certificate_date: Date of certificate generation.

    Returns:
        Path: Path to the generated PDF.
    """

    file_path = OUTPUT_DIR / f"certificate_{certificate_id}.pdf"

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height)
    )

    # ---------------------------------------------------------
    # Background
    # ---------------------------------------------------------

    pdf.setFillColor(colors.white)

    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )

    # ---------------------------------------------------------
    # Outer border
    # ---------------------------------------------------------

    pdf.setStrokeColor(colors.HexColor("#1F4E79"))
    pdf.setLineWidth(4)

    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60,
        fill=0,
        stroke=1
    )

    # ---------------------------------------------------------
    # Inner border
    # ---------------------------------------------------------

    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(1.5)

    pdf.rect(
        42,
        42,
        page_width - 84,
        page_height - 84,
        fill=0,
        stroke=1
    )

    # ---------------------------------------------------------
    # Organization name
    # ---------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#1F4E79"))
    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 78,
        "BULK CERTIFICATE GENERATOR"
    )

    # ---------------------------------------------------------
    # Main title
    # ---------------------------------------------------------

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 30)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 125,
        "CERTIFICATE OF COMPLETION"
    )

    # ---------------------------------------------------------
    # Decorative line
    # ---------------------------------------------------------

    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(2)

    line_width = 220

    pdf.line(
        (page_width - line_width) / 2,
        page_height - 140,
        (page_width + line_width) / 2,
        page_height - 140
    )

    # ---------------------------------------------------------
    # Introductory text
    # ---------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 15)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 180,
        "This certificate is proudly presented to"
    )

    # ---------------------------------------------------------
    # Recipient name
    # ---------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#1F4E79"))

    recipient_font_size = 27

    if len(recipient_name) > 30:
        recipient_font_size = 22
    elif len(recipient_name) > 22:
        recipient_font_size = 24

    pdf.setFont(
        "Helvetica-Bold",
        recipient_font_size
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 230,
        recipient_name
    )

    # ---------------------------------------------------------
    # Completion text
    # ---------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 15)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 270,
        "for successfully completing"
    )

    # ---------------------------------------------------------
    # Course name
    # ---------------------------------------------------------

    pdf.setFillColor(colors.black)

    course_font_size = 21

    if len(course_name) > 35:
        course_font_size = 17
    elif len(course_name) > 25:
        course_font_size = 19

    pdf.setFont(
        "Helvetica-Bold",
        course_font_size
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 310,
        course_name
    )

    # ---------------------------------------------------------
    # Certificate information
    # ---------------------------------------------------------

    if certificate_date is None:
        from django.utils import timezone

        certificate_date = timezone.now().date()

    formatted_date = certificate_date.strftime("%d %B %Y")

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        75,
        95,
        f"Certificate ID: CERT-{certificate_id:05d}"
    )

    pdf.drawRightString(
        page_width - 75,
        95,
        f"Date: {formatted_date}"
    )

    # ---------------------------------------------------------
    # Signature section
    # ---------------------------------------------------------

    pdf.setStrokeColor(colors.HexColor("#555555"))
    pdf.setLineWidth(1)

    left_signature_x = 200
    right_signature_x = page_width - 200

    # Signature lines
    pdf.line(
        left_signature_x - 70,
        75,
        left_signature_x + 70,
        75
    )

    pdf.line(
        right_signature_x - 70,
        75,
        right_signature_x + 70,
        75
    )

    # Signature labels
    # Only ONE copy of each label is drawn.
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 10)

    pdf.drawCentredString(
        left_signature_x,
        58,
        "Authorized Signature"
    )

    pdf.drawCentredString(
        right_signature_x,
        58,
        "Certificate Authority"
    )

    # ---------------------------------------------------------
    # Save PDF
    # ---------------------------------------------------------

    pdf.save()

    return file_path