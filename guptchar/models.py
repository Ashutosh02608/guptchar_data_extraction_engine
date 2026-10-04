"""
Pydantic data models for Guptchar Core Data Extraction Engine.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExecutiveContact(BaseModel):
    """Schema for individual executive and leadership contact."""
    name: str = Field(default="N/A", description="Full name of executive or key contact")
    title: str = Field(default="N/A", description="Corporate or regulatory job title")
    phone: str = Field(default="N/A", description="Direct or department phone number")
    email: str = Field(default="N/A", description="Direct or corporate email address")
    source: str = Field(default="Website", description="Data provenance (e.g. 'SEC Filing / Website', 'SEC EDGAR', 'Website')")


class CompanyLead(BaseModel):
    """
    Standard schema for company lead representation.
    Matches exact JSON structure specified in Guptchar V1.0 specifications.
    """
    company_name: str = Field(default="N/A", description="Official name of the business entity")
    address: str = Field(default="N/A", description="Physical registered address or headquarters")
    website: str = Field(default="N/A", description="Official company website URL")
    generic_contact_number: str = Field(
        default="N/A",
        description="Gatekeeper or generic office contact number from Google Maps / website"
    )
    primary_email: str = Field(default="N/A", description="Primary support or corporate email")
    one_sentence_description: str = Field(
        default="N/A",
        description="Concise one-sentence summary of company operations"
    )
    executives_and_contacts: List[ExecutiveContact] = Field(
        default_factory=list,
        description="List of identified executive officers, leadership, and contacts"
    )

    def to_clean_dict(self) -> dict:
        """Export to dictionary ensuring all N/A fallbacks and clean formatting."""
        return {
            "company_name": self.company_name or "N/A",
            "address": self.address or "N/A",
            "website": self.website or "N/A",
            "generic_contact_number": self.generic_contact_number or "N/A",
            "primary_email": self.primary_email or "N/A",
            "one_sentence_description": self.one_sentence_description or "N/A",
            "executives_and_contacts": [
                {
                    "name": ec.name or "N/A",
                    "title": ec.title or "N/A",
                    "phone": ec.phone or "N/A",
                    "email": ec.email or "N/A",
                    "source": ec.source or "Website",
                }
                for ec in self.executives_and_contacts
            ],
        }


class SearchInput(BaseModel):
    """Input parameters for the Guptchar lead extraction pipeline."""
    country: str = Field(..., description="Target Country (e.g., 'United States')", json_schema_extra={"example": "United States"})
    city: str = Field(..., description="Target City (e.g., 'New York')", json_schema_extra={"example": "New York"})
    sector_keyword: str = Field(
        ...,
        description="Sector or search keyword (e.g., 'Hedge Funds', 'Financial Compliance')",
        json_schema_extra={"example": "Hedge Funds"}
    )
    limit: int = Field(default=5, ge=1, le=50, description="Max number of leads to extract")
    export_json: bool = Field(default=True, description="Save output to JSON file locally")
    export_pdf: bool = Field(default=True, description="Export results as formatted PDF report")
