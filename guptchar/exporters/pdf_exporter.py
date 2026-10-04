"""
PDF Exporter for Guptchar Core Data Extraction Engine.
Generates a structured, executive-ready PDF report presenting lead cards and executive dossiers.
"""

from datetime import datetime
import logging
import os
import re
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from guptchar.models import CompanyLead

logger = logging.getLogger("guptchar.exporters.pdf")


def generate_pdf_filename(city: str, output_dir: str = ".") -> str:
    """Generate filename adhering to: guptchar_output_[city]_[timestamp].pdf."""
    clean_city = re.sub(r"[^a-zA-Z0-9_-]", "_", city.lower().strip())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"guptchar_output_{clean_city}_{timestamp}.pdf"
    return os.path.join(output_dir, filename)


class NumberedCanvas:
    """Two-pass canvas for dynamic total page count in footer."""

    def __init__(self, canvas, doc):
        self.canvas = canvas
        self.doc = doc


def _draw_page_decorations(canvas, doc):
    """Draw header and footer on each page."""
    canvas.saveState()
    # Header bar
    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.rect(0, 10.7 * inch, 8.5 * inch, 0.4 * inch, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(0.5 * inch, 10.82 * inch, "GUPTCHAR CORE ENGINE V1.0")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(8.0 * inch, 10.82 * inch, "B2B LEAD DOSSIER & REGULATORY EXTRACTION")

    # Footer bar
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(0.5 * inch, 0.5 * inch, 8.0 * inch, 0.5 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.5 * inch, 0.35 * inch, "CONFIDENTIAL - PRODUCED BY GUPTCHAR AUTOMATED INTELLIGENCE")
    canvas.drawRightString(8.0 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def export_to_pdf(
    leads: List[CompanyLead],
    city: str,
    country: str = "United States",
    sector_keyword: str = "Financial Sector",
    output_path: str = None,
) -> str:
    """
    Generate a formatted PDF report with clean cards/tables showing:
    Company Name, Generic/Gatekeeper Phone, Primary Email, Address, One-Sentence Summary,
    and a list of key Executives/Contacts.
    """
    if not output_path:
        output_path = generate_pdf_filename(city)

    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    doc = SimpleDocTemplate(
        abs_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.7 * inch,
        author="Ashutosh",
        creator="Guptchar Engine (Lead: Ashutosh)",
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )

    company_title_style = ParagraphStyle(
        "CompanyTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
    )

    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )

    value_style = ParagraphStyle(
        "ValueStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    desc_style = ParagraphStyle(
        "DescStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    th_style = ParagraphStyle(
        "THStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    td_style = ParagraphStyle(
        "TDStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
    )

    badge_sec = ParagraphStyle(
        "BadgeSEC",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1e3a8a"),
    )

    badge_web = ParagraphStyle(
        "BadgeWEB",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#065f46"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("GUPTCHAR LEAD DOSSIER", title_style))
    story.append(Spacer(1, 4))
    gen_time = datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")
    meta_text = (
        f"<b>Target Region:</b> {city}, {country} &nbsp;|&nbsp; "
        f"<b>Sector / Query:</b> {sector_keyword} &nbsp;|&nbsp; "
        f"<b>Total Entities:</b> {len(leads)} &nbsp;|&nbsp; "
        f"<b>Generated:</b> {gen_time}"
    )
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#0284c7"),
            spaceBefore=0,
            spaceAfter=12,
        )
    )

    if not leads:
        story.append(Paragraph("<i>No entities extracted for the specified criteria.</i>", desc_style))

    # Lead Cards
    for idx, lead in enumerate(leads, start=1):
        lead_elements = []

        # Card Title Header
        lead_elements.append(
            Paragraph(f"<b>#{idx}. {lead.company_name}</b>", company_title_style)
        )
        lead_elements.append(Spacer(1, 4))

        # Description Callout Box
        desc_text = f"<b>One-Sentence Summary:</b> {lead.one_sentence_description or 'N/A'}"
        desc_table = Table(
            [[Paragraph(desc_text, desc_style)]],
            colWidths=[7.5 * inch],
        )
        desc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        lead_elements.append(desc_table)
        lead_elements.append(Spacer(1, 5))

        # Core Metadata Table (Phone, Email, Website, Address)
        meta_data = [
            [
                Paragraph("Generic / Gatekeeper Phone:", label_style),
                Paragraph(lead.generic_contact_number or "N/A", value_style),
                Paragraph("Primary Email:", label_style),
                Paragraph(lead.primary_email or "N/A", value_style),
            ],
            [
                Paragraph("Official Website:", label_style),
                Paragraph(lead.website or "N/A", value_style),
                Paragraph("Address:", label_style),
                Paragraph(lead.address or "N/A", value_style),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[1.8 * inch, 1.95 * inch, 1.35 * inch, 2.4 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        lead_elements.append(meta_table)
        lead_elements.append(Spacer(1, 6))

        # Key Executives and Contacts Table
        execs = lead.executives_and_contacts
        if execs:
            exec_rows = [
                [
                    Paragraph("Name", th_style),
                    Paragraph("Title / Role", th_style),
                    Paragraph("Direct Phone", th_style),
                    Paragraph("Email", th_style),
                    Paragraph("Source Provenance", th_style),
                ]
            ]
            for ec in execs:
                badge = badge_sec if "sec" in (ec.source or "").lower() else badge_web
                exec_rows.append(
                    [
                        Paragraph(f"<b>{ec.name}</b>", td_style),
                        Paragraph(ec.title or "N/A", td_style),
                        Paragraph(ec.phone or "N/A", td_style),
                        Paragraph(ec.email or "N/A", td_style),
                        Paragraph(ec.source or "N/A", badge),
                    ]
                )

            exec_table = Table(
                exec_rows,
                colWidths=[1.7 * inch, 2.0 * inch, 1.25 * inch, 1.35 * inch, 1.2 * inch],
            )
            exec_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f1f5f9")]),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            lead_elements.append(exec_table)
        else:
            no_exec_msg = Paragraph("<i>No specific executive contacts indexed for this entity.</i>", desc_style)
            lead_elements.append(no_exec_msg)

        lead_elements.append(Spacer(1, 14))
        lead_elements.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#e2e8f0"),
                spaceBefore=0,
                spaceAfter=14,
            )
        )

        story.append(KeepTogether(lead_elements))

    # Build document
    doc.build(story, onFirstPage=_draw_page_decorations, onLaterPages=_draw_page_decorations)
    logger.info(f"[Export: PDF] Dossier PDF generated successfully: {abs_path}")
    return abs_path
