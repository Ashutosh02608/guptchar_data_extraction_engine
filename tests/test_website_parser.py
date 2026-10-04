"""
Unit tests for Stage B website extraction logic.
"""

from bs4 import BeautifulSoup
from guptchar.scrapers.website_scraper import WebsiteEnrichmentScraper
from guptchar.models import CompanyLead


def test_email_validation():
    scraper = WebsiteEnrichmentScraper()
    assert scraper._is_valid_email("contact@apexadvisory.com")
    assert scraper._is_valid_email("john.doe@hedgefund.org")
    assert not scraper._is_valid_email("icon@2x.png")
    assert not scraper._is_valid_email("user@example.com")
    assert not scraper._is_valid_email("invalid-email")


def test_description_extraction():
    scraper = WebsiteEnrichmentScraper()
    html = """
    <html>
      <head>
        <meta name="description" content="Apex Advisory delivers institutional regulatory compliance and advisory solutions for global hedge funds.">
      </head>
      <body>
        <p>Welcome to our firm.</p>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    desc = scraper._extract_description(soup)
    assert "Apex Advisory delivers institutional regulatory compliance" in desc


def test_team_card_extraction():
    scraper = WebsiteEnrichmentScraper()
    html = """
    <div class="team-grid">
      <div class="team-card">
        <h3>Sarah Jenkins</h3>
        <p class="role">Chief Compliance Officer</p>
        <p>Email: sjenkins@apexadvisory.com</p>
        <p>Direct: +1 212-555-0188</p>
      </div>
      <div class="team-card">
        <h3>Michael Chang</h3>
        <p class="role">Managing Director</p>
        <p>Email: mchang@apexadvisory.com</p>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    contacts = scraper._extract_team_members(soup, "https://apexadvisory.com")
    assert len(contacts) == 2

    c1 = next(c for c in contacts if "Sarah" in c.name)
    assert c1.name == "Sarah Jenkins"
    assert "Compliance" in c1.title
    assert c1.email == "sjenkins@apexadvisory.com"
    assert "212-555-0188" in c1.phone
    assert c1.source == "Website"
