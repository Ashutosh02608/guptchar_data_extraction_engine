"""
JSON Exporter for Guptchar Core Data Extraction Engine.
Saves structured leads to guptchar_output_[city]_[timestamp].json adhering to the required schema.
"""

from datetime import datetime
import json
import logging
import os
import re
from typing import List

from guptchar.config import OUTPUT_DIR
from guptchar.models import CompanyLead

logger = logging.getLogger("guptchar.exporters.json")


def generate_json_filename(city: str, output_dir: str = None) -> str:
    """Generate filename adhering to: guptchar_output_[city]_[timestamp].json."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    clean_city = re.sub(r"[^a-zA-Z0-9_-]", "_", city.lower().strip())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"guptchar_output_{clean_city}_{timestamp}.json"
    return os.path.join(output_dir, filename)


def export_to_json(leads: List[CompanyLead], city: str, output_path: str = None) -> str:
    """
    Export list of CompanyLead objects to JSON file.
    Returns the absolute path of the generated JSON file.
    """
    if not output_path:
        output_path = generate_json_filename(city)

    # Format data cleanly- Ashutosh
    data = [lead.to_clean_dict() for lead in leads]

    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"[Export: JSON] Saved {len(leads)} leads to: {abs_path}")
    return abs_path
