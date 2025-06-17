"""
Pydantic models for FastAPI request/response serialization.
These models handle data validation and serialization for the API layer.
"""

from pydantic import BaseModel, Field


class PropertyResponse(BaseModel):
    """
    Pydantic model for property responses in the FastAPI layer.
    This handles serialization from SQLAlchemy models to JSON/dict.
    """

    id: int
    name: str = Field(..., description="Property name")
    location: str = Field(..., description="Property location")
    type: str = Field(..., description="Property type (Apartment, House, etc.)")
    price: str = Field(..., description="Property price")
    details: str = Field(..., description="Additional property details")

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allows conversion from SQLAlchemy models


class PropertyCreate(BaseModel):
    """
    Pydantic model for creating new properties.
    Used for POST requests to add new properties.
    """

    name: str = Field(..., min_length=1, max_length=255, description="Property name")
    location: str = Field(
        ..., min_length=1, max_length=255, description="Property location"
    )
    type: str = Field(..., min_length=1, max_length=100, description="Property type")
    price: str = Field(..., min_length=1, max_length=100, description="Property price")
    details: str = Field(
        ..., min_length=1, max_length=500, description="Property details"
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
