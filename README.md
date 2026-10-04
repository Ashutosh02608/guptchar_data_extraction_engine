# Guptchar Core Data Extraction Engine (V1.0) 🚀

> **High-Precision B2B Lead-Generation, Website Enrichment, and Financial Regulatory Data Extraction Engine.**  
> Budget: **$0** (Open-source libraries, free-tier SEC EDGAR REST API, and zero-cost Python stack).

---

## 📌 Architecture Overview

Guptchar is an automated, modular Python intelligence pipeline designed to extract, enrich, and structure high-value prospect data across three continuous stages:

```
[ Input: Country, City, Sector/Keyword ]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  STAGE A: Google Maps Scraper                          │
│  - Headless stealth Chrome automation (CDP masked)     │
│  - Extracts: Company Name, Address, Website,           │
│    Generic Contact Number (gatekeeper_number)          │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE B: Website Scraper & Anti-Bot Evasion           │
│  - Chrome TLS fingerprint impersonation (curl_cffi)    │
│  - Cloudflare / WAF challenge bypass (cloudscraper)    │
│  - Subpage discovery: /contact, /about, /team          │
│  - Extracts: Primary corporate email, team contacts,   │
│    and one-sentence company description                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  STAGE C: Financial Regulatory Filings Look-up         │
│  - Active when sector relates to Finance/Compliance    │
│  - Queries official US SEC EDGAR REST API              │
│  - Parses Form ADV, Form D, and EDGAR Submissions      │
│  - Discovers C-Suite Executives (CEO, CCO, MD)         │
│  - Tags data provenance ("SEC Filing / Website")       │
└──────────────────────────┬─────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  OUTPUT: JSON EXPORT     │  │  OUTPUT: FORMATTED PDF   │
│  guptchar_output_*.json  │  │  Executive Dossier Card  │
│  Strict Schema Conformance│  │  ReportLab Table Layout │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 📊 Standard JSON Data Schema

All extracted records are formatted strictly into the required JSON schema with missing field fallback to `"N/A"`:

```json
{
  "company_name": "Magnitude Capital LLC",
  "address": "MetLife Building, 200 Park Ave, New York, NY 10166, United States",
  "website": "http://www.magnitudecapital.com/",
  "generic_contact_number": "+1 212-915-3900",
  "primary_email": "contact@magnitudecapital.com",
  "one_sentence_description": "For over twenty years, Magnitude Capital has built and managed global, multi-strategy hedge fund portfolios and related vehicles.",
  "executives_and_contacts": [
    {
      "name": "Benjamin Appen",
      "title": "Executive Officer",
      "phone": "345-949-3977",
      "email": "N/A",
      "source": "SEC Filing / Website"
    },
    {
      "name": "Andrew Messinger",
      "title": "General Counsel / Executive Officer",
      "phone": "345-949-3977",
      "email": "N/A",
      "source": "SEC Filing / Website"
    }
  ]
}
```

---

## 🛠️ Technology Stack ($0 Budget Setup)

- **Language:** Python 3.10+
- **Browser Automation:** Selenium (headless stealth mode with CDP masking)
- **Anti-Bot & Stealth Network Layer:** `curl_cffi` (Chrome JA3/TLS browser impersonation) & `cloudscraper`
- **Regulatory API:** Official US SEC EDGAR REST API (`https://efts.sec.gov` & `https://data.sec.gov`)
- **PDF Generation:** ReportLab (`SimpleDocTemplate`, custom styled tables, headers, footers)
- **API & Web Service:** FastAPI + Uvicorn + Pydantic v2
- **Testing:** Pytest

---

## 🚀 Quickstart & Installation

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Ashutosh02608/guptchar_data_extraction_engine.git
cd guptchar_data_extraction_engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 CLI Usage Guide

Run the extraction engine directly from the command line:

```bash
# Basic run: Hedge Funds in New York
python main.py cli --country "United States" --city "New York" --sector "Hedge Funds" --limit 5

# Financial Compliance in Boston
python main.py cli --country "United States" --city "Boston" --sector "Financial Compliance" --limit 3

# Private Equity in Chicago with custom output file names
python main.py cli -c "United States" -C "Chicago" -s "Private Equity" -l 5 --json-output custom_leads.json --pdf-output dossier.pdf
```

### CLI Arguments

| Argument | Shorthand | Description | Default |
|---|---|---|---|
| `--country` | `-c` | Target Country | `"United States"` |
| `--city` | `-C` | Target City | *(Required)* |
| `--sector` / `--query` | `-s` | Sector or keyword search | *(Required)* |
| `--limit` | `-l` | Maximum entities to extract | `5` |
| `--no-json` | | Disable JSON export | `False` |
| `--no-pdf` | | Disable PDF export | `False` |
| `--json-output` | | Custom JSON destination path | `Auto-generated` |
| `--pdf-output` | | Custom PDF destination path | `Auto-generated` |
| `--no-headless` | | Run Chrome in visible mode | `False` (Headless) |
| `--verbose` | `-v` | Enable debug logs | `False` |

---

## 🌐 FastAPI Server & Interactive Web Console

Guptchar includes an interactive executive dashboard and REST API server.

### Start the Server:

```bash
python main.py serve --port 8000
```

Open your browser to: **`http://localhost:8000`**

### REST API Endpoints

- **`POST /api/v1/extract`**: Accepts a JSON body and triggers the extraction pipeline.
  ```json
  {
    "country": "United States",
    "city": "New York",
    "sector_keyword": "Hedge Funds",
    "limit": 3,
    "export_json": true,
    "export_pdf": true
  }
  ```
- **`GET /api/v1/download/json/{filename}`**: Download generated JSON files.
- **`GET /api/v1/download/pdf/{filename}`**: Download formatted PDF report.
- **`GET /api/v1/health`**: Health check.
- **`GET /docs`**: Interactive Swagger / OpenAPI documentation.

---

## 📄 PDF Dossier Export Preview

The generated PDF report includes:
- Corporate running header & confidential disclaimer footer with page numbers.
- Query metadata badge (Region, Sector, Extraction Timestamp, Total Entities).
- Company Cards:
  * Company Name & One-Sentence Summary Callout.
  * Metadata Table: Generic / Gatekeeper Phone, Primary Email, Official Website, Physical Address.
  * Executive Contacts Table: Name, Role / Title, Direct Phone, Email, Provenance Badge (`SEC Filing / Website` vs `Website`).

---

## 🧪 Testing & Verification

Run the comprehensive unit and integration test suite:

```bash
pytest tests/ -v
```

All 13 tests cover:
- Pydantic schema validation & `N/A` fallback handling
- JSON and ReportLab PDF file generation
- Anti-bot website regex & DOM team card extraction
- SEC EDGAR Form D XML parsing & financial sector keyword trigger
- FastAPI endpoints & static web console assets

---

## 📂 Project Structure

```
guptchar/
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                     # Unified CLI / Server runner
├── guptchar/
│   ├── __init__.py             # Version and package info
│   ├── config.py               # Constants, timeouts, headers
│   ├── models.py               # Pydantic schemas (CompanyLead, etc.)
│   ├── pipeline.py             # GuptcharPipeline orchestrator
│   ├── cli.py                  # CLI command implementation
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── maps_scraper.py     # Stage A: Google Maps scraper
│   │   ├── website_scraper.py  # Stage B: Website enrichment & stealth
│   │   └── sec_edgar.py        # Stage C: SEC EDGAR regulatory filings
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── json_exporter.py    # Standard JSON exporter
│   │   └── pdf_exporter.py     # ReportLab formatted PDF exporter
│   └── api/
│       ├── __init__.py
│       ├── server.py           # FastAPI REST API
│       └── static/
│           ├── index.html      # Interactive Executive Console
│           ├── app.css         # Glassmorphism dark mode styles
│           └── app.js          # Pipeline client logic
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_exporters.py
    ├── test_website_parser.py
    ├── test_sec_parser.py
    └── test_api.py
```

---

## ⚖️ License & Compliance
Built for institutional intelligence and B2B market research using publicly available web interfaces and the official US Securities and Exchange Commission (SEC) EDGAR public records.

**Repository:** [github.com/Ashutosh02608/guptchar_data_extraction_engine](https://github.com/Ashutosh02608/guptchar_data_extraction_engine)  
**Author:** Ashutosh ([@Ashutosh02608](https://github.com/Ashutosh02608))
