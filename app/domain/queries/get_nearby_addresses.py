from dataclasses import dataclass
import logging
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import InvalidCoordinateError
from app.domain.services.geo import calculate_bounding_box, haversine_distance
from app.models.address import AddressModel
from app.schemas.address import NearbyAddressRead

logger = logging.getLogger("eastvantage.address_book.queries.nearby")


@dataclass(frozen=True)
class GetNearbyAddressesQuery:
    latitude: float
    longitude: float
    radius_km: float = 5.0
    limit: int = 20


class GetNearbyAddressesHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle(self, query: GetNearbyAddressesQuery) -> list[NearbyAddressRead]:
        """Perform a two-stage proximity search using an indexed bounding box and Haversine sorting.

        Algorithm & Decision Points:
            Standard SQLite lacks built-in trigonometry functions or R-tree spatial indexes
            without requiring SpatiaLite C extensions. A full table scan computing Haversine
            in Python scales as O(N).
            This handler uses a two-stage filter:
            1. Stage 1 (Index Pruning): Calculates a bounding box and filters records in SQL
               using the ix_addresses_coordinates index (O(log N + K) candidates).
            2. Stage 2 (Exact Distance): Computes exact Haversine distances on candidates,
               filters out bounding box corner points beyond the circular radius, and sorts
               ascending by proximity.

        Edge Cases:
            - Antimeridian crossing: When the bounding box spans across +/-180 longitude,
              the query automatically uses a disjunctive OR condition.
        """
        if not (-90.0 <= query.latitude <= 90.0):
            raise InvalidCoordinateError(
                f"Latitude {query.latitude} is outside valid bounds [-90.0, 90.0]."
            )
        if not (-180.0 <= query.longitude <= 180.0):
            raise InvalidCoordinateError(
                f"Longitude {query.longitude} is outside valid bounds [-180.0, 180.0]."
            )
        if query.radius_km <= 0:
            raise InvalidCoordinateError("Search radius must be strictly positive.")

        box = calculate_bounding_box(
            latitude=query.latitude,
            longitude=query.longitude,
            radius_km=query.radius_km,
        )

        stmt = select(AddressModel).where(
            AddressModel.latitude >= box.min_lat,
            AddressModel.latitude <= box.max_lat,
        )

        if box.is_antimeridian_wrapped:
            stmt = stmt.where(
                or_(
                    AddressModel.longitude >= box.min_lon,
                    AddressModel.longitude <= box.max_lon,
                )
            )
        else:
            stmt = stmt.where(
                AddressModel.longitude >= box.min_lon,
                AddressModel.longitude <= box.max_lon,
            )

        stmt = stmt.execution_options(populate_existing=False)
        result = await self.session.execute(stmt)
        candidates = result.scalars().all()

        nearby_results: list[tuple[float, AddressModel]] = []
        for candidate in candidates:
            dist = haversine_distance(
                lat1=query.latitude,
                lon1=query.longitude,
                lat2=candidate.latitude,
                lon2=candidate.longitude,
            )
            if dist <= query.radius_km:
                nearby_results.append((dist, candidate))

        nearby_results.sort(key=lambda pair: pair[0])
        sliced_results = nearby_results[: query.limit]

        output: list[NearbyAddressRead] = []
        for dist, candidate in sliced_results:
            address_dto = NearbyAddressRead(
                id=candidate.id,
                street=candidate.street,
                city=candidate.city,
                state_province=candidate.state_province,
                postal_code=candidate.postal_code,
                country=candidate.country,
                latitude=candidate.latitude,
                longitude=candidate.longitude,
                created_at=candidate.created_at,
                updated_at=candidate.updated_at,
                distance_km=round(dist, 3),
            )
            output.append(address_dto)

        logger.info(
            f"Proximity search origin=({query.latitude}, {query.longitude}) "
            f"radius={query.radius_km}km candidates={len(candidates)} matches={len(output)}"
        )
        return output
