"""
Guptchar Pipeline Orchestrator.
Coordinates Stage A (Google Maps) -> Stage B (Website Enrichment) -> Stage C (SEC EDGAR Regulatory Look-up),
and exports structured intelligence to JSON and formatted PDF.
"""

import logging
import time
from typing import Dict, List, Optional

from guptchar.exporters import export_to_json, export_to_pdf
from guptchar.models import CompanyLead, SearchInput
from guptchar.scrapers import GoogleMapsScraper, SecEdgarScraper, WebsiteEnrichmentScraper

logger = logging.getLogger("guptchar.pipeline")


class GuptcharPipeline:
    """
    End-to-end data extraction and intelligence pipeline for Guptchar V1.0.
    """

    def __init__(self, headless: bool = True):
        self.maps_scraper = GoogleMapsScraper(headless=headless)
        self.website_scraper = WebsiteEnrichmentScraper()
        self.sec_scraper = SecEdgarScraper()

    def run(
        self,
        country: str,
        city: str,
        sector_keyword: str,
        limit: int = 5,
        export_json_file: bool = True,
        export_pdf_file: bool = True,
        json_output_path: Optional[str] = None,
        pdf_output_path: Optional[str] = None,
    ) -> Dict:
        """
        Execute full extraction workflow across Stage A, Stage B, and Stage C.
        """
        start_time = time.time()
        logger.info(
            f"=== Launching Guptchar Core Engine V1.0 ===\n"
            f"Region: {city}, {country} | Sector: {sector_keyword} | Target: {limit}"
        )

        # Stage A: Google Maps Scraper
        logger.info("--> STAGE A: Google Maps Local Extraction")
        stage_a_leads = self.maps_scraper.search(
            country=country,
            city=city,
            sector_keyword=sector_keyword,
            limit=limit,
        )

        enriched_leads: List[CompanyLead] = []

        # Stage B & C: Iterative Enrichment per Lead
        for idx, lead in enumerate(stage_a_leads, start=1):
            logger.info(f"--> Processing Lead #{idx}/{len(stage_a_leads)}: '{lead.company_name}'")

            # Stage B: Website Enrichment
            logger.info(f"   [Stage B] Visiting website: {lead.website}")
            lead = self.website_scraper.enrich_lead(lead)

            # Stage C: SEC EDGAR Regulatory Look-up (Finance Sector Switch)
            if self.sec_scraper.is_financial_sector(sector_keyword):
                logger.info(f"   [Stage C] Financial sector detected. Querying SEC EDGAR for: {lead.company_name}")
                lead = self.sec_scraper.enrich_lead(lead, sector_keyword)
            else:
                logger.info(f"   [Stage C] Sector '{sector_keyword}' is non-financial. Skipping SEC switch.")

            enriched_leads.append(lead)

        # Exports
        json_file = None
        pdf_file = None

        if export_json_file and enriched_leads:
            logger.info("--> Generating Structured JSON Output")
            json_file = export_to_json(enriched_leads, city=city, output_path=json_output_path)

        if export_pdf_file and enriched_leads:
            logger.info("--> Generating Formatted Executive PDF Report")
            pdf_file = export_to_pdf(
                enriched_leads,
                city=city,
                country=country,
                sector_keyword=sector_keyword,
                output_path=pdf_output_path,
            )

        elapsed = round(time.time() - start_time, 2)
        logger.info(
            f"=== Guptchar Pipeline Completed in {elapsed}s ===\n"
            f"Total Leads: {len(enriched_leads)} | JSON: {json_file} | PDF: {pdf_file}"
        )

        return {
            "status": "success",
            "country": country,
            "city": city,
            "sector_keyword": sector_keyword,
            "total_leads": len(enriched_leads),
            "elapsed_seconds": elapsed,
            "json_file": json_file,
            "pdf_file": pdf_file,
            "leads": [lead.to_clean_dict() for lead in enriched_leads],
        }
