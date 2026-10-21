from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AddressNotFoundError
from app.models.address import AddressModel
from app.schemas.address import AddressRead

logger = logging.getLogger("eastvantage.address_book.commands.update")


@dataclass(frozen=True)
class UpdateAddressCommand:
    address_id: str
    street: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_partial: bool = False


class UpdateAddressHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, command: UpdateAddressCommand) -> AddressRead:
        """Apply state mutations, distinguishing full replacement (PUT) from selective updates (PATCH)."""
        stmt = select(AddressModel).where(AddressModel.id == command.address_id)
        result = await self.session.execute(stmt)
        address = result.scalar_one_or_none()

        if address is None:
            logger.warning(f"Update failed: address not found id={command.address_id}")
            raise AddressNotFoundError(address_id=command.address_id)

        if command.is_partial:
            if command.street is not None:
                address.street = command.street
            if command.city is not None:
                address.city = command.city
            if command.state_province is not None:
                address.state_province = command.state_province
            if command.postal_code is not None:
                address.postal_code = command.postal_code
            if command.country is not None:
                address.country = command.country
            if command.latitude is not None:
                address.latitude = command.latitude
            if command.longitude is not None:
                address.longitude = command.longitude
        else:
            if command.street is not None:
                address.street = command.street
            if command.city is not None:
                address.city = command.city
            if command.state_province is not None:
                address.state_province = command.state_province
            if command.postal_code is not None:
                address.postal_code = command.postal_code
            if command.country is not None:
                address.country = command.country
            if command.latitude is not None:
                address.latitude = command.latitude
            if command.longitude is not None:
                address.longitude = command.longitude

        address.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(address)

        logger.info(f"Updated address id={address.id} partial={command.is_partial}")
        return AddressRead.model_validate(address)
