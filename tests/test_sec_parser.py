"""
Unit tests for Stage C SEC EDGAR Regulatory parser.
"""

from unittest.mock import patch, MagicMock
from guptchar.scrapers.sec_edgar import SecEdgarScraper
from guptchar.models import CompanyLead, ExecutiveContact


def test_is_financial_sector():
    assert SecEdgarScraper.is_financial_sector("Hedge Funds") is True
    assert SecEdgarScraper.is_financial_sector("Financial Compliance") is True
    assert SecEdgarScraper.is_financial_sector("Private Equity") is True
    assert SecEdgarScraper.is_financial_sector("Software Development") is False
    assert SecEdgarScraper.is_financial_sector("Italian Bakery") is False


def test_clean_company_name():
    scraper = SecEdgarScraper()
    assert scraper._clean_company_name("Apex Advisory LLC") == "Apex Advisory"
    assert scraper._clean_company_name("Magnitude Capital, LLC") == "Magnitude Capital,"
    assert scraper._clean_company_name("Bridgewater Associates LP") == "Bridgewater Associates"


def test_parse_form_d_xml():
    scraper = SecEdgarScraper()
    sample_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <edgarSubmission>
      <primaryData>
        <relatedPersonInfo>
          <relatedPersonName>
            <firstName>Marcus</firstName>
            <lastName>Vance</lastName>
          </relatedPersonName>
          <relatedPersonRelationshipList>
            <relationship>Executive Officer</relationship>
            <relationshipClarification>Chief Compliance Officer</relationshipClarification>
          </relatedPersonRelationshipList>
        </relatedPersonInfo>
      </primaryData>
    </edgarSubmission>
    """

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = sample_xml

    with patch("curl_cffi.requests.get", return_value=mock_resp):
        execs = scraper._parse_form_d_xml("123456", "0000123456-24-000001", "primary_doc.xml", "+1 212-555-0100")
        assert len(execs) == 1
        assert execs[0].name == "Marcus Vance"
        assert execs[0].title == "Chief Compliance Officer"
        assert execs[0].phone == "+1 212-555-0100"
        assert execs[0].source == "SEC Filing / Website"
