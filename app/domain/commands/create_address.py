from dataclasses import dataclass
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.address import AddressModel
from app.schemas.address import AddressRead

logger = logging.getLogger("eastvantage.address_book.commands.create")


@dataclass(frozen=True)
class CreateAddressCommand:
    street: str
    city: str
    state_province: str
    postal_code: str
    country: str
    latitude: float
    longitude: float


class CreateAddressHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, command: CreateAddressCommand) -> AddressRead:
        address_id = str(uuid.uuid4())
        address = AddressModel(
            id=address_id,
            street=command.street,
            city=command.city,
            state_province=command.state_province,
            postal_code=command.postal_code,
            country=command.country,
            latitude=command.latitude,
            longitude=command.longitude,
        )

        self.session.add(address)
        await self.session.commit()
        await self.session.refresh(address)

        logger.info(
            f"Created address id={address.id} at ({address.latitude}, {address.longitude})"
        )
        return AddressRead.model_validate(address)
