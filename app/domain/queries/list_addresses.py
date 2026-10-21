from dataclasses import dataclass
import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.address import AddressModel
from app.schemas.address import AddressListResponse, AddressRead

logger = logging.getLogger("eastvantage.address_book.queries.list")


@dataclass(frozen=True)
class ListAddressesQuery:
    offset: int = 0
    limit: int = 20


class ListAddressesHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, query: ListAddressesQuery) -> AddressListResponse:
        count_stmt = select(func.count(AddressModel.id))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        items_stmt = (
            select(AddressModel)
            .order_by(AddressModel.created_at.desc())
            .offset(query.offset)
            .limit(query.limit)
            .execution_options(populate_existing=False)
        )
        items_result = await self.session.execute(items_stmt)
        addresses = items_result.scalars().all()

        items = [AddressRead.model_validate(addr) for addr in addresses]
        logger.debug(f"Retrieved {len(items)} addresses out of {total} total.")
        return AddressListResponse(
            items=items,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )
