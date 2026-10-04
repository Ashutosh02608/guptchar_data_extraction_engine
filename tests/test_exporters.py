"""
Unit tests for JSON and PDF exporters.
"""

import json
import os
from guptchar.exporters import export_to_json, export_to_pdf
from guptchar.models import CompanyLead, ExecutiveContact


def test_json_and_pdf_export(tmp_path):
    lead = CompanyLead(
        company_name="Apex Advisory LLC",
        address="123 Wall St, New York, NY",
        website="https://apexadvisory.com",
        generic_contact_number="+1-212-555-0100",
        primary_email="contact@apexadvisory.com",
        one_sentence_description="Provides SEC compliance and hedge fund regulatory consulting.",
        executives_and_contacts=[
            ExecutiveContact(
                name="John Doe",
                title="Chief Compliance Officer",
                phone="+1-212-555-0199",
                email="jdoe@apexadvisory.com",
                source="SEC Filing / Website",
            )
        ],
    )

    json_target = str(tmp_path / "test_output.json")
    json_path = export_to_json([lead], city="New York", output_path=json_target)
    assert os.path.exists(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["company_name"] == "Apex Advisory LLC"
    assert data[0]["executives_and_contacts"][0]["name"] == "John Doe"

    pdf_target = str(tmp_path / "test_output.pdf")
    pdf_path = export_to_pdf(
        [lead],
        city="New York",
        country="United States",
        sector_keyword="Hedge Funds",
        output_path=pdf_target,
    )
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
