from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.domain.commands.create_address import CreateAddressHandler
from app.domain.commands.delete_address import DeleteAddressHandler
from app.domain.commands.update_address import UpdateAddressHandler
from app.domain.queries.get_address import GetAddressByIdHandler
from app.domain.queries.get_nearby_addresses import GetNearbyAddressesHandler
from app.domain.queries.list_addresses import ListAddressesHandler


def get_create_address_handler(
    session: AsyncSession = Depends(get_db_session),
) -> CreateAddressHandler:
    return CreateAddressHandler(session=session)


def get_update_address_handler(
    session: AsyncSession = Depends(get_db_session),
) -> UpdateAddressHandler:
    return UpdateAddressHandler(session=session)


def get_delete_address_handler(
    session: AsyncSession = Depends(get_db_session),
) -> DeleteAddressHandler:
    return DeleteAddressHandler(session=session)


def get_address_by_id_handler(
    session: AsyncSession = Depends(get_db_session),
) -> GetAddressByIdHandler:
    return GetAddressByIdHandler(session=session)


def get_list_addresses_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ListAddressesHandler:
    return ListAddressesHandler(session=session)


def get_nearby_addresses_handler(
    session: AsyncSession = Depends(get_db_session),
) -> GetNearbyAddressesHandler:
    return GetNearbyAddressesHandler(session=session)
