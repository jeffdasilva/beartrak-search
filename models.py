"""
Pydantic models for FastAPI request/response serialization.
These models handle data validation and serialization for the API layer.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RFPResponse(BaseModel):
    """
    Pydantic model for RFP responses in the FastAPI layer.
    This handles serialization from SQLAlchemy models to JSON/dict.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(..., description="RFP name")
    url: str | None = Field(None, description="Optional URL for more information")
    description: str | None = Field(None, description="RFP description")
    updated_at: datetime = Field(..., description="When the RFP was last updated")


class RFPCreate(BaseModel):
    """
    Pydantic model for creating new RFPs.
    Used for POST requests to add new RFPs.
    """

    name: str = Field(..., min_length=1, max_length=255, description="RFP name")
    url: str | None = Field(None, max_length=2048, description="Optional URL")
    description: str | None = Field(
        None, description="Optional RFP description for search purposes"
    )


class RFPUpdate(BaseModel):
    """
    Pydantic model for updating existing RFPs.
    Used for PUT/PATCH requests to update RFPs.
    """

    name: str | None = Field(None, min_length=1, max_length=255, description="RFP name")
    url: str | None = Field(None, max_length=2048, description="Optional URL")
    description: str | None = Field(
        None, description="Optional RFP description for search purposes"
    )


class SearchRequest(BaseModel):
    """
    Pydantic model for search requests.
    """

    query: str = Field(..., min_length=1, description="Search query")


class HealthResponse(BaseModel):
    """
    Pydantic model for health check responses.
    """

    status: str
    service: str
    database_status: str = Field(
        default="unknown", description="Database connection status"
    )
