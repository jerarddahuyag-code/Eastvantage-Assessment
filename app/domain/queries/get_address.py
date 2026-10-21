from dataclasses import dataclass
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AddressNotFoundError
from app.models.address import AddressModel
from app.schemas.address import AddressRead

logger = logging.getLogger("eastvantage.address_book.queries.get")


@dataclass(frozen=True)
class GetAddressByIdQuery:
    address_id: str


class GetAddressByIdHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, query: GetAddressByIdQuery) -> AddressRead:
        """Fetch address by ID with read-only execution options to bypass identity tracking overhead."""
        stmt = (
            select(AddressModel)
            .where(AddressModel.id == query.address_id)
            .execution_options(populate_existing=False)
        )
        result = await self.session.execute(stmt)
        address = result.scalar_one_or_none()

        if address is None:
            logger.info(f"Query returned no record for id={query.address_id}")
            raise AddressNotFoundError(address_id=query.address_id)

        return AddressRead.model_validate(address)
