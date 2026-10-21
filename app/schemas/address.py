from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CoordinatesBase(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees (-90.0 to 90.0)",
        examples=[48.8566],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees (-180.0 to 180.0)",
        examples=[2.3522],
    )


class AddressBase(CoordinatesBase):
    street: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Street name, number, or building details",
        examples=["10 Rue de Rivoli"],
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City or municipality",
        examples=["Paris"],
    )
    state_province: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="State, province, or administrative region",
        examples=["Île-de-France"],
    )
    postal_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Postal or ZIP code",
        examples=["75001"],
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country name or ISO code",
        examples=["France"],
    )

    @field_validator("street", "city", "state_province", "postal_code", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace and reject blank strings before validation."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Value cannot be blank or consist solely of whitespace.")
            return stripped
        return value


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    street: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state_province: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)

    @field_validator("street", "city", "state_province", "postal_code", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Value cannot be blank or consist solely of whitespace.")
            return stripped
        return value


class AddressRead(AddressBase):
    id: str = Field(..., description="Unique UUID identifier for the address")
    created_at: datetime = Field(..., description="Timestamp when address was created")
    updated_at: datetime = Field(..., description="Timestamp when address was last updated")

    model_config = ConfigDict(from_attributes=True)


class NearbyAddressRead(AddressRead):
    distance_km: float = Field(
        ...,
        ge=0.0,
        description="Calculated radial distance in kilometers from the query coordinate",
        examples=[3.42],
    )


class AddressListResponse(BaseModel):
    items: list[AddressRead] = Field(default_factory=list, description="List of addresses")
    total: int = Field(..., ge=0, description="Total number of matching addresses")
    limit: int = Field(..., ge=1, description="Page size limit")
    offset: int = Field(..., ge=0, description="Page offset")
