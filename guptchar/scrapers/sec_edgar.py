"""
Stage C: Financial Regulatory Filings Look-up (SEC EDGAR)
Queries official US SEC EDGAR REST API and parses regulatory filings (Form ADV, Form D, 10-K, DEF 14A)
for registered C-suite executives, Key Personnel (CEO, CCO, Managing Director), and direct contact details.
"""

import logging
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

from curl_cffi import requests as curl_requests

from guptchar.config import FINANCE_SECTOR_KEYWORDS, HTTP_TIMEOUT, SEC_USER_AGENT
from guptchar.models import CompanyLead, ExecutiveContact

logger = logging.getLogger("guptchar.scrapers.sec_edgar")

# Executive titles prioritized in financial filings
FINANCE_TITLES = [
    "Chief Executive Officer",
    "Chief Compliance Officer",
    "Managing Director",
    "Managing Partner",
    "General Counsel",
    "Chief Operating Officer",
    "Chief Financial Officer",
    "Chief Investment Officer",
    "Executive Officer",
    "Principal",
    "Partner",
    "Director",
    "President",
]


class SecEdgarScraper:
    """
    Scraper for official SEC EDGAR public regulatory repositories.
    """

    def __init__(self, user_agent: str = SEC_USER_AGENT, timeout: int = HTTP_TIMEOUT):
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.timeout = timeout

    @staticmethod
    def is_financial_sector(sector_keyword: str) -> bool:
        """Determine whether the search query relates to the financial/compliance sector."""
        if not sector_keyword:
            return False
        clean_kw = sector_keyword.lower()
        return any(f_kw in clean_kw for f_kw in FINANCE_SECTOR_KEYWORDS)

    def lookup_company(self, company_name: str) -> List[ExecutiveContact]:
        """
        Query SEC EDGAR for regulatory filings associated with the company name
        and extract registered Key Personnel and C-Suite Executives.
        """
        if not company_name or company_name == "N/A":
            return []

        clean_name = self._clean_company_name(company_name)
        logger.info(f"[Stage C: SEC] Searching SEC EDGAR regulatory database for: '{clean_name}'")

        executives: List[ExecutiveContact] = []
        try:
            # 1. Search SEC EFTS (EDGAR Full-Text Search)
            search_url = (
                f"https://efts.sec.gov/LATEST/search-index"
                f"?q={urllib.parse.quote(clean_name)}"
                f"&category=custom&forms=ADV,D,10-K,DEF%2014A"
            )
            resp = curl_requests.get(
                search_url,
                headers=self.headers,
                impersonate="chrome",
                timeout=self.timeout,
            )

            if resp.status_code != 200:
                logger.warning(f"[Stage C: SEC] EFTS search returned status {resp.status_code}")
                return executives

            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            logger.info(f"[Stage C: SEC] Found {len(hits)} matching SEC filings for '{clean_name}'")

            if not hits:
                return executives

            # Track unique company CIKs discovered
            seen_ciks = set()
            cik_candidates = []
            for hit in hits[:8]:
                src = hit.get("_source", {})
                ciks = src.get("ciks", [])
                adsh = src.get("adsh", "")
                form = src.get("form", "")
                if ciks and ciks[0] not in seen_ciks:
                    seen_ciks.add(ciks[0])
                    cik_candidates.append((ciks[0], adsh, form))

            # Query SEC Submissions for top matching CIKs
            for cik, adsh, form in cik_candidates[:3]:
                sec_execs, sec_phone = self._process_cik_filings(cik, clean_name)
                for se in sec_execs:
                    if not any(e.name.lower() == se.name.lower() for e in executives):
                        executives.append(se)
                if len(executives) >= 5:
                    break

        except Exception as e:
            logger.warning(f"[Stage C: SEC] Exception during SEC EDGAR query for '{company_name}': {e}")

        logger.info(f"[Stage C: SEC] Completed SEC extraction. Found {len(executives)} registered executives.")
        return executives

    def enrich_lead(self, lead: CompanyLead, sector_keyword: str) -> CompanyLead:
        """
        Conditionally enrich a CompanyLead with SEC regulatory filing data
        if the search sector falls under financial/compliance.
        """
        if not self.is_financial_sector(sector_keyword):
            logger.info(f"[Stage C: SEC] Sector '{sector_keyword}' is non-financial. Skipping SEC regulatory switch.")
            return lead

        sec_execs = self.lookup_company(lead.company_name)

        if sec_execs:
            existing_names = {e.name.lower() for e in lead.executives_and_contacts}
            for se in sec_execs:
                if se.name.lower() not in existing_names:
                    existing_names.add(se.name.lower())
                    lead.executives_and_contacts.append(se)

            # If phone or email is present in SEC and missing in lead, backfill
            for se in sec_execs:
                if (not lead.generic_contact_number or lead.generic_contact_number == "N/A") and se.phone != "N/A":
                    lead.generic_contact_number = se.phone
                if (not lead.primary_email or lead.primary_email == "N/A") and se.email != "N/A":
                    lead.primary_email = se.email

        return lead

    def _process_cik_filings(self, cik_str: str, company_name: str) -> Tuple[List[ExecutiveContact], str]:
        """
        Fetch submission details and parse Form D/ADV for related persons & executives.
        """
        executives: List[ExecutiveContact] = []
        company_phone = "N/A"

        cik_padded = cik_str.zfill(10)
        sub_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

        try:
            resp = curl_requests.get(
                sub_url,
                headers=self.headers,
                impersonate="chrome",
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                return executives, company_phone

            sub = resp.json()
            company_phone = sub.get("phone") or "N/A"

            recent = sub.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accessions = recent.get("accessionNumber", [])
            primary_docs = recent.get("primaryDocument", [])

            cik_int = str(int(cik_str))

            for idx in range(min(5, len(forms))):
                form_type = forms[idx]
                adsh = accessions[idx]
                doc_name = primary_docs[idx]

                # If Form D (Standard offering form for hedge funds/private equity listing all related persons)
                if form_type.startswith("D"):
                    d_execs = self._parse_form_d_xml(cik_int, adsh, doc_name, company_phone)
                    for de in d_execs:
                        if not any(e.name.lower() == de.name.lower() for e in executives):
                            executives.append(de)
                    if len(executives) >= 3:
                        break

        except Exception as e:
            logger.debug(f"[Stage C: SEC] Error processing CIK {cik_str}: {e}")

        return executives, company_phone

    def _parse_form_d_xml(
        self, cik_int: str, adsh: str, doc_name: str, company_phone: str
    ) -> List[ExecutiveContact]:
        """Parse Form D XML for Related Persons (Executive Officers, Directors, Promoters)."""
        executives: List[ExecutiveContact] = []
        adsh_no_hyphen = adsh.replace("-", "")

        # Target raw XML
        raw_doc_name = doc_name.replace("xslFormDX01/", "")
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{adsh_no_hyphen}/{raw_doc_name}"

        try:
            resp = curl_requests.get(
                doc_url,
                headers=self.headers,
                impersonate="chrome",
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                return executives

            root = ET.fromstring(resp.content)
            for rp in root.iter():
                if "relatedPersonInfo" in rp.tag:
                    item_dict = {
                        child.tag.split("}")[-1]: (child.text.strip() if child.text else "")
                        for child in rp.iter()
                    }

                    first_name = item_dict.get("firstName", "")
                    last_name = item_dict.get("lastName", "")
                    entity_name = item_dict.get("entityName", "")

                    # Check if person vs corporate entity
                    name = f"{first_name} {last_name}".strip()
                    if not name or name.lower() in ["n/a", "none"]:
                        if entity_name:
                            name = entity_name
                        else:
                            continue

                    # Skip corporate manager entries as person names
                    if any(corp_suffix in name.lower() for corp_suffix in [" llc", " ltd", " inc", " corp", " partners lp"]):
                        continue

                    # Determine title
                    clarification = item_dict.get("relationshipClarification", "")
                    relationship = item_dict.get("relationship", "")
                    is_exec = item_dict.get("isExecutiveOfficer", "").lower() == "true"
                    is_dir = item_dict.get("isDirector", "").lower() == "true"

                    title = clarification
                    if not title:
                        if is_exec and is_dir:
                            title = "Executive Officer & Director"
                        elif is_exec:
                            title = "Executive Officer"
                        elif is_dir:
                            title = "Director"
                        elif relationship:
                            title = relationship
                        else:
                            title = "Managing Director"

                    executives.append(
                        ExecutiveContact(
                            name=name,
                            title=title,
                            phone=company_phone if company_phone != "N/A" else "N/A",
                            email="N/A",
                            source="SEC Filing / Website",
                        )
                    )

        except Exception as e:
            logger.debug(f"[Stage C: SEC] Error parsing Form D XML from {doc_url}: {e}")

        return executives

    def _clean_company_name(self, name: str) -> str:
        """Strip suffixes like LLC, LP, Inc. for broader search matching."""
        cleaned = re.sub(
            r"\b(LLC|L\.L\.C\.|LP|L\.P\.|Inc\.|Inc|Corp\.|Corp|Ltd\.|Ltd|Co\.|Co)\b",
            "",
            name,
            flags=re.IGNORECASE,
        )
        return cleaned.strip()
