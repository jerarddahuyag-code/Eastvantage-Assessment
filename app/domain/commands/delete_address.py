from dataclasses import dataclass
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AddressNotFoundError
from app.models.address import AddressModel

logger = logging.getLogger("eastvantage.address_book.commands.delete")


@dataclass(frozen=True)
class DeleteAddressCommand:
    address_id: str


class DeleteAddressHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, command: DeleteAddressCommand) -> None:
        stmt = select(AddressModel).where(AddressModel.id == command.address_id)
        result = await self.session.execute(stmt)
        address = result.scalar_one_or_none()

        if address is None:
            logger.warning(f"Delete failed: address not found id={command.address_id}")
            raise AddressNotFoundError(address_id=command.address_id)

        await self.session.delete(address)
        await self.session.commit()
        logger.info(f"Deleted address id={command.address_id}")
