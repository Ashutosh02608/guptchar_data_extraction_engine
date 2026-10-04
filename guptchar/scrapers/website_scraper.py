"""
Stage B: Website Scraper & Anti-Bot Evasion
Crawls target websites, bypasses Cloudflare/bot mitigations using curl_cffi and cloudscraper,
and extracts primary corporate emails, phone numbers, one-sentence descriptions, and leadership profiles.
"""

import logging
import re
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
import cloudscraper

from guptchar.config import HTTP_TIMEOUT, STANDARD_HEADERS
from guptchar.models import CompanyLead, ExecutiveContact

logger = logging.getLogger("guptchar.scrapers.website")

# Common regex patterns
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)

# Common leadership title keywords
TITLE_KEYWORDS = [
    "Chief Executive Officer",
    "CEO",
    "Chief Compliance Officer",
    "CCO",
    "Managing Director",
    "Partner",
    "Managing Partner",
    "General Partner",
    "Founder",
    "Co-Founder",
    "President",
    "Chief Operating Officer",
    "COO",
    "Chief Financial Officer",
    "CFO",
    "Chief Investment Officer",
    "CIO",
    "General Counsel",
    "Head of Compliance",
    "Portfolio Manager",
    "Principal",
    "Director",
]

# Excluded image/binary email patterns
DISALLOWED_EMAIL_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js"}


class WebsiteEnrichmentScraper:
    """
    Stealth web scraper and data extractor for company websites.
    """

    def __init__(self, timeout: int = HTTP_TIMEOUT):
        self.timeout = timeout
        self.cloud_scraper = cloudscraper.create_scraper()

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL using curl_cffi (Chrome TLS fingerprint)
        with fallback to cloudscraper.
        """
        if not url or url == "N/A" or not url.startswith("http"):
            return None

        # Strategy 1: curl_cffi with Chrome impersonation
        try:
            resp = curl_requests.get(
                url,
                headers=STANDARD_HEADERS,
                impersonate="chrome",
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,
            )
            if resp.status_code == 200 and resp.text:
                return resp.text
        except Exception as e:
            logger.debug(f"[Stage B: Website] curl_cffi failed for {url}: {e}. Retrying with cloudscraper...")

        # Strategy 2: cloudscraper for Cloudflare JS challenges
        try:
            c_resp = self.cloud_scraper.get(url, timeout=self.timeout, verify=False)
            if c_resp.status_code == 200 and c_resp.text:
                return c_resp.text
        except Exception as e:
            logger.debug(f"[Stage B: Website] cloudscraper failed for {url}: {e}")

        return None

    def enrich_lead(self, lead: CompanyLead) -> CompanyLead:
        """
        Enrich a CompanyLead with website description, emails, and executive profiles.
        """
        if not lead.website or lead.website == "N/A":
            logger.info(f"[Stage B: Website] No website available for '{lead.company_name}'. Skipping enrichment.")
            return lead

        base_url = lead.website.strip()
        if not base_url.startswith("http"):
            base_url = "https://" + base_url

        logger.info(f"[Stage B: Website] Enriching lead '{lead.company_name}' via {base_url}")

        homepage_html = self.fetch_page(base_url)
        if not homepage_html:
            logger.warning(f"[Stage B: Website] Could not access homepage for {base_url}")
            return lead

        soup = BeautifulSoup(homepage_html, "html.parser")

        # 1. Extract One-Sentence Description if not already present
        if not lead.one_sentence_description or lead.one_sentence_description == "N/A":
            lead.one_sentence_description = self._extract_description(soup)

        # 2. Discover relevant subpages (/contact, /about, /team, /leadership, etc.)
        target_subpages = self._discover_subpages(soup, base_url)

        # 3. Collect emails, phones, and executives across key pages
        all_emails: Set[str] = set()
        all_phones: Set[str] = set()
        discovered_executives: List[ExecutiveContact] = []

        # Parse homepage first
        page_emails, page_phones = self._extract_emails_and_phones(soup, base_url)
        all_emails.update(page_emails)
        all_phones.update(page_phones)
        discovered_executives.extend(self._extract_team_members(soup, base_url))

        # Parse discovered subpages (max 4 subpages to maintain speed)
        for page_type, sub_url in list(target_subpages.items())[:4]:
            logger.debug(f"[Stage B: Website] Crawling {page_type} page: {sub_url}")
            sub_html = self.fetch_page(sub_url)
            if sub_html:
                sub_soup = BeautifulSoup(sub_html, "html.parser")
                s_emails, s_phones = self._extract_emails_and_phones(sub_soup, base_url)
                all_emails.update(s_emails)
                all_phones.update(s_phones)
                discovered_executives.extend(self._extract_team_members(sub_soup, base_url))

        # 4. Resolve Primary Email
        if all_emails:
            lead.primary_email = self._select_primary_email(all_emails, base_url)

        # 5. Resolve Generic Contact Number if still N/A
        if (not lead.generic_contact_number or lead.generic_contact_number == "N/A") and all_phones:
            lead.generic_contact_number = list(all_phones)[0]

        # 6. Merge Discovered Executives
        existing_names = {e.name.lower() for e in lead.executives_and_contacts}
        for exec_c in discovered_executives:
            if exec_c.name.lower() not in existing_names and len(exec_c.name.split()) >= 2:
                existing_names.add(exec_c.name.lower())
                lead.executives_and_contacts.append(exec_c)

        logger.info(
            f"[Stage B: Website] Finished enrichment for '{lead.company_name}'. "
            f"Email: {lead.primary_email}, Contacts: {len(lead.executives_and_contacts)}"
        )
        return lead

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract a clean one-sentence company description."""
        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if meta_desc and meta_desc.get("content"):
            content = meta_desc["content"].strip()
            # Truncate to first sentence or clean concise statement
            sentences = re.split(r"(?<=[.!?])\s+", content)
            if sentences and len(sentences[0]) > 20:
                return sentences[0][:300]
            return content[:300]

        # Hero paragraph or first substantial paragraph
        for p in soup.find_all("p"):
            text = p.get_text(" ", strip=True)
            if len(text) > 40 and not any(k in text.lower() for k in ["cookie", "javascript", "browser", "rights reserved"]):
                sentences = re.split(r"(?<=[.!?])\s+", text)
                return sentences[0][:300] if sentences else text[:300]

        return "N/A"

    def _discover_subpages(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Find links to /contact, /about, /team, /leadership, etc."""
        subpages: Dict[str, str] = {}
        parsed_base = urllib.parse.urlparse(base_url)
        base_domain = parsed_base.netloc.lower().replace("www.", "")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            full_url = urllib.parse.urljoin(base_url, href)
            parsed_link = urllib.parse.urlparse(full_url)
            link_domain = parsed_link.netloc.lower().replace("www.", "")

            # Keep links on the same domain
            if link_domain and link_domain != base_domain:
                continue

            path = parsed_link.path.lower()
            text = a.get_text(" ", strip=True).lower()

            if ("contact" in path or "contact" in text) and "contact" not in subpages:
                subpages["contact"] = full_url
            elif ("about" in path or "about" in text or "who-we-are" in path) and "about" not in subpages:
                subpages["about"] = full_url
            elif ("team" in path or "team" in text or "people" in path or "leadership" in path or "management" in path) and "team" not in subpages:
                subpages["team"] = full_url

        return subpages

    def _extract_emails_and_phones(self, soup: BeautifulSoup, base_url: str) -> Tuple[Set[str], Set[str]]:
        """Extract valid email addresses and phone numbers from HTML."""
        emails: Set[str] = set()
        phones: Set[str] = set()

        # 1. Search mailto: links
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().startswith("mailto:"):
                raw_mail = href[7:].split("?")[0].strip()
                if self._is_valid_email(raw_mail):
                    emails.add(raw_mail.lower())
            elif href.lower().startswith("tel:"):
                raw_tel = href[4:].split("?")[0].strip()
                if len(re.sub(r"\D", "", raw_tel)) >= 7:
                    phones.add(raw_tel)

        # 2. Text-based Regex extraction
        text = soup.get_text(" ", strip=True)
        raw_emails = EMAIL_REGEX.findall(text)
        for em in raw_emails:
            clean_em = em.strip().lower()
            if self._is_valid_email(clean_em):
                emails.add(clean_em)

        raw_phones = PHONE_REGEX.findall(text)
        for ph in raw_phones:
            cleaned = ph.strip()
            digits = re.sub(r"\D", "", cleaned)
            if 10 <= len(digits) <= 13:
                phones.add(cleaned)

        return emails, phones

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format and filter out false positives / assets."""
        if not email or "@" not in email:
            return False
        if any(email.lower().endswith(ext) for ext in DISALLOWED_EMAIL_EXTENSIONS):
            return False
        user, domain = email.split("@", 1)
        if len(user) < 1 or len(domain) < 3 or "." not in domain:
            return False
        # Filter dummy/placeholder templates
        if any(d in domain.lower() for d in ["example.com", "domain.com", "yourdomain", "sentry.io", "wixpress.com"]):
            return False
        return True

    def _select_primary_email(self, emails: Set[str], base_url: str) -> str:
        """Heuristically select best corporate primary email."""
        parsed = urllib.parse.urlparse(base_url)
        domain = parsed.netloc.lower().replace("www.", "")

        # Prefer standard corporate prefixes
        preferred_prefixes = ["contact", "info", "inquiries", "ir", "investors", "hello", "general", "support", "office"]
        for pref in preferred_prefixes:
            for email in emails:
                if email.startswith(pref + "@") and domain in email:
                    return email

        # Then prefer any email matching the company domain
        for email in emails:
            if domain in email:
                return email

        # Fallback to first valid email
        return sorted(list(emails))[0]

    def _extract_team_members(self, soup: BeautifulSoup, base_url: str) -> List[ExecutiveContact]:
        """
        Extract leadership and C-level team members from DOM cards and structure.
        """
        contacts: List[ExecutiveContact] = []
        seen_names = set()

        # Target card containers
        cards = soup.select(
            ".team-member, .team-item, .person, .leadership-card, .profile-card, "
            ".bio-card, div[class*='team'], div[class*='leadership'], div[class*='executive']"
        )

        for card in cards:
            text = card.get_text("\n", strip=True)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if not lines:
                continue

            name = "N/A"
            title = "N/A"
            phone = "N/A"
            email = "N/A"

            # Check headings for name
            headings = card.find_all(["h2", "h3", "h4", "h5", "strong"])
            for h in headings:
                h_text = h.get_text(strip=True)
                words = h_text.split()
                if 2 <= len(words) <= 4 and not any(kw.lower() in h_text.lower() for kw in TITLE_KEYWORDS):
                    name = h_text
                    break

            if name == "N/A" and len(lines) >= 1:
                first_line = lines[0]
                if 2 <= len(first_line.split()) <= 4:
                    name = first_line

            # Find matching title
            for line in lines:
                for kw in TITLE_KEYWORDS:
                    if kw.lower() in line.lower() and len(line) < 60:
                        title = line
                        break
                if title != "N/A":
                    break

            # Find email inside card
            card_emails = EMAIL_REGEX.findall(text)
            for ce in card_emails:
                if self._is_valid_email(ce):
                    email = ce.lower()
                    break

            # Find phone inside card
            card_phones = PHONE_REGEX.findall(text)
            if card_phones:
                phone = card_phones[0].strip()

            if name != "N/A" and title != "N/A" and name.lower() not in seen_names:
                seen_names.add(name.lower())
                contacts.append(
                    ExecutiveContact(
                        name=name,
                        title=title,
                        phone=phone,
                        email=email,
                        source="Website",
                    )
                )

        return contacts
