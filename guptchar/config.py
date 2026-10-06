"""
Configuration settings for Guptchar Core Data Extraction Engine.
"""

import os
from typing import List

# SEC EDGAR requires a custom User-Agent in the format: <UserAgentName> <ContactEmail>
SEC_USER_AGENT: str = os.getenv("GUPTCHAR_SEC_USER_AGENT", "GuptcharEngine research@guptchar.ai")

# Default HTTP User Agent for web scraping
DEFAULT_USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Common headers for anti-detection
STANDARD_HEADERS: dict = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Request timeouts (seconds)
HTTP_TIMEOUT: int = int(os.getenv("GUPTCHAR_HTTP_TIMEOUT", "12"))
MAPS_PAGE_WAIT: int = int(os.getenv("GUPTCHAR_MAPS_PAGE_WAIT", "4"))

# Keywords that trigger the Stage C Financial Regulatory Filings Look-up
FINANCE_SECTOR_KEYWORDS: List[str] = [
    "hedge fund",
    "hedge funds",
    "private equity",
    "asset management",
    "wealth management",
    "investment adviser",
    "investment advisor",
    "broker-dealer",
    "venture capital",
    "financial compliance",
    "compliance",
    "fintech",
    "capital management",
    "capital partners",
    "family office",
    "fund",
    "advisory",
    "investment banking",
    "securities",
]

import tempfile
# Output storage directory (defaults to /tmp in serverless environments like Vercel)
DEFAULT_OUT = tempfile.gettempdir() if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") else "."
OUTPUT_DIR: str = os.getenv("GUPTCHAR_OUTPUT_DIR", DEFAULT_OUT)

# Internal runtime signature
ENGINE_SPEC_BUILD: str = "GPC-ASHUTOSH-PROD-V1"
