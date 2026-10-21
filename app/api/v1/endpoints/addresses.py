from fastapi import APIRouter, Depends, Path, Query, status
from app.api.deps import (
    get_address_by_id_handler,
    get_create_address_handler,
    get_delete_address_handler,
    get_list_addresses_handler,
    get_nearby_addresses_handler,
    get_update_address_handler,
)
from app.core.config import get_settings
from app.domain.commands.create_address import CreateAddressCommand, CreateAddressHandler
from app.domain.commands.delete_address import DeleteAddressCommand, DeleteAddressHandler
from app.domain.commands.update_address import UpdateAddressCommand, UpdateAddressHandler
from app.domain.queries.get_address import GetAddressByIdHandler, GetAddressByIdQuery
from app.domain.queries.get_nearby_addresses import (
    GetNearbyAddressesHandler,
    GetNearbyAddressesQuery,
)
from app.domain.queries.list_addresses import ListAddressesHandler, ListAddressesQuery
from app.schemas.address import (
    AddressCreate,
    AddressListResponse,
    AddressRead,
    AddressUpdate,
    NearbyAddressRead,
)

settings = get_settings()
router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post(
    "",
    response_model=AddressRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create address",
    description="Validate coordinates and location fields, then create a new address record.",
)
async def create_address(
    payload: AddressCreate,
    handler: CreateAddressHandler = Depends(get_create_address_handler),
) -> AddressRead:
    command = CreateAddressCommand(
        street=payload.street,
        city=payload.city,
        state_province=payload.state_province,
        postal_code=payload.postal_code,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    return await handler.handle(command)


@router.get(
    "",
    response_model=AddressListResponse,
    status_code=status.HTTP_200_OK,
    summary="List addresses",
    description="Retrieve paginated address records ordered by creation date descending.",
)
async def list_addresses(
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=settings.default_query_limit,
        ge=1,
        le=settings.max_query_limit,
        description="Maximum records to return",
    ),
    handler: ListAddressesHandler = Depends(get_list_addresses_handler),
) -> AddressListResponse:
    query = ListAddressesQuery(offset=offset, limit=limit)
    return await handler.handle(query)


@router.get(
    "/nearby",
    response_model=list[NearbyAddressRead],
    status_code=status.HTTP_200_OK,
    summary="Search addresses within distance",
    description=(
        "Retrieve addresses within a radial distance (in kilometers) from given coordinates, "
        "sorted ascending by calculated distance."
    ),
)
async def get_nearby_addresses(
    latitude: float = Query(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude of origin coordinate (-90.0 to 90.0)",
        examples=[48.8566],
    ),
    longitude: float = Query(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude of origin coordinate (-180.0 to 180.0)",
        examples=[2.3522],
    ),
    radius_km: float = Query(
        default=settings.default_search_radius_km,
        gt=0.0,
        le=settings.max_search_radius_km,
        description="Search radius in kilometers",
        examples=[5.0],
    ),
    limit: int = Query(
        default=settings.default_query_limit,
        ge=1,
        le=settings.max_query_limit,
        description="Maximum matching records to return",
    ),
    handler: GetNearbyAddressesHandler = Depends(get_nearby_addresses_handler),
) -> list[NearbyAddressRead]:
    query = GetNearbyAddressesQuery(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
    )
    return await handler.handle(query)


@router.get(
    "/{address_id}",
    response_model=AddressRead,
    status_code=status.HTTP_200_OK,
    summary="Get address by ID",
    description="Fetch a single address by its UUID identifier.",
)
async def get_address_by_id(
    address_id: str = Path(..., description="Unique UUID identifier of the address"),
    handler: GetAddressByIdHandler = Depends(get_address_by_id_handler),
) -> AddressRead:
    query = GetAddressByIdQuery(address_id=address_id)
    return await handler.handle(query)


@router.put(
    "/{address_id}",
    response_model=AddressRead,
    status_code=status.HTTP_200_OK,
    summary="Replace address",
    description="Completely replace all fields of an existing address record.",
)
async def replace_address(
    address_id: str = Path(..., description="Unique UUID identifier of the address"),
    payload: AddressCreate = ...,
    handler: UpdateAddressHandler = Depends(get_update_address_handler),
) -> AddressRead:
    command = UpdateAddressCommand(
        address_id=address_id,
        street=payload.street,
        city=payload.city,
        state_province=payload.state_province,
        postal_code=payload.postal_code,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_partial=False,
    )
    return await handler.handle(command)


@router.patch(
    "/{address_id}",
    response_model=AddressRead,
    status_code=status.HTTP_200_OK,
    summary="Partially update address",
    description="Update specified fields of an existing address record without overwriting unsupplied fields.",
)
async def update_address_partial(
    address_id: str = Path(..., description="Unique UUID identifier of the address"),
    payload: AddressUpdate = ...,
    handler: UpdateAddressHandler = Depends(get_update_address_handler),
) -> AddressRead:
    command = UpdateAddressCommand(
        address_id=address_id,
        street=payload.street,
        city=payload.city,
        state_province=payload.state_province,
        postal_code=payload.postal_code,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_partial=True,
    )
    return await handler.handle(command)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete address",
    description="Remove an address record by identifier.",
)
async def delete_address(
    address_id: str = Path(..., description="Unique UUID identifier of the address"),
    handler: DeleteAddressHandler = Depends(get_delete_address_handler),
) -> None:
    command = DeleteAddressCommand(address_id=address_id)
    await handler.handle(command)
