from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AddressModel(Base):
    __tablename__ = "addresses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state_province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Composite index enables fast bounding box range scans without full table scans in SQLite
    __table_args__ = (
        Index("ix_addresses_coordinates", "latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return (
            f"<AddressModel(id={self.id}, street={self.street}, "
            f"city={self.city}, country={self.country}, "
            f"lat={self.latitude}, lon={self.longitude})>"
        )
