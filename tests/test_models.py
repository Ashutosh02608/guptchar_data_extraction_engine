"""
Unit tests for data models and schema conformance.
"""

from guptchar.models import CompanyLead, ExecutiveContact


def test_executive_contact_defaults():
    ec = ExecutiveContact()
    assert ec.name == "N/A"
    assert ec.title == "N/A"
    assert ec.phone == "N/A"
    assert ec.email == "N/A"
    assert ec.source == "Website"


def test_company_lead_schema_compliance():
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

    clean_dict = lead.to_clean_dict()
    assert clean_dict["company_name"] == "Apex Advisory LLC"
    assert clean_dict["generic_contact_number"] == "+1-212-555-0100"
    assert clean_dict["primary_email"] == "contact@apexadvisory.com"
    assert clean_dict["address"] == "123 Wall St, New York, NY"
    assert clean_dict["website"] == "https://apexadvisory.com"
    assert clean_dict["one_sentence_description"] == "Provides SEC compliance and hedge fund regulatory consulting."
    assert len(clean_dict["executives_and_contacts"]) == 1

    exec_contact = clean_dict["executives_and_contacts"][0]
    assert exec_contact["name"] == "John Doe"
    assert exec_contact["title"] == "Chief Compliance Officer"
    assert exec_contact["phone"] == "+1-212-555-0199"
    assert exec_contact["email"] == "jdoe@apexadvisory.com"
    assert exec_contact["source"] == "SEC Filing / Website"


def test_company_lead_fallback_to_na():
    lead = CompanyLead()
    clean = lead.to_clean_dict()
    assert clean["company_name"] == "N/A"
    assert clean["address"] == "N/A"
    assert clean["website"] == "N/A"
    assert clean["generic_contact_number"] == "N/A"
    assert clean["primary_email"] == "N/A"
    assert clean["one_sentence_description"] == "N/A"
    assert clean["executives_and_contacts"] == []
