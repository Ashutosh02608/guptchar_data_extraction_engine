"""
FastAPI Server for Guptchar Core Data Extraction Engine.
Provides RESTful endpoints for extraction jobs, file downloads, and an interactive intelligence console.
"""

import os
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from guptchar.config import OUTPUT_DIR
from guptchar.models import SearchInput
from guptchar.pipeline import GuptcharPipeline

app = FastAPI(
    title="Guptchar Core Data Extraction Engine",
    description="High-precision lead generation, website enrichment, and financial regulatory filings extractor API.",
    version="1.0.0",
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = GuptcharPipeline(headless=True)
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "public")
STATIC_DIR = PUBLIC_DIR if os.path.exists(PUBLIC_DIR) else os.path.join(os.path.dirname(__file__), "static")


@app.get("/api/v1/health")
@app.get("/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Guptchar Core Extraction Engine",
        "version": "1.0.0",
    }


@app.post("/api/v1/extract")
@app.post("/v1/extract")
async def extract_leads(payload: SearchInput):
    """
    Trigger end-to-end extraction pipeline:
    - Stage A: Google Maps Scraper
    - Stage B: Website Enrichment & Anti-bot Crawl
    - Stage C: SEC EDGAR Regulatory Look-up (Finance Sector Switch)
    - Structured JSON and PDF export
    """
    try:
        results = pipeline_instance.run(
            country=payload.country,
            city=payload.city,
            sector_keyword=payload.sector_keyword,
            limit=payload.limit,
            export_json_file=payload.export_json,
            export_pdf_file=payload.export_pdf,
        )

        # Include relative download links for generated files
        json_path = results.get("json_file")
        pdf_path = results.get("pdf_file")

        download_urls = {}
        if json_path and os.path.exists(json_path):
            download_urls["json_download"] = f"/api/v1/download/json/{os.path.basename(json_path)}"
        if pdf_path and os.path.exists(pdf_path):
            download_urls["pdf_download"] = f"/api/v1/download/pdf/{os.path.basename(pdf_path)}"

        return {
            **results,
            **download_urls,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction pipeline failure: {str(e)}",
        )


@app.get("/api/v1/download/json/{filename}")
@app.get("/v1/download/json/{filename}")
async def download_json(filename: str):
    """Download generated JSON result file."""
    # Sanitize filename
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, clean_filename)
    if not os.path.exists(file_path):
        file_path = os.path.abspath(clean_filename)

    if not os.path.exists(file_path) or not clean_filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="JSON export file not found.")

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=clean_filename,
    )


@app.get("/api/v1/download/pdf/{filename}")
@app.get("/v1/download/pdf/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF dossier file."""
    # Sanitize filename
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, clean_filename)
    if not os.path.exists(file_path):
        file_path = os.path.abspath(clean_filename)

    if not os.path.exists(file_path) or not clean_filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="PDF dossier file not found.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=clean_filename,
    )


# Mount static directory for interactive web UI
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
