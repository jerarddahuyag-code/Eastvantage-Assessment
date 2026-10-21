from dataclasses import dataclass
import math

EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class BoundingBox:
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    is_antimeridian_wrapped: bool = False


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate the great-circle distance between two points in kilometers.

    Algorithm & Formula:
        Uses the Haversine formula on a spherical Earth model with IUGG mean radius
        (R = 6371.0088 km). The formula uses atan2 over arccos to prevent floating-point
        precision loss for antipodal and near-zero distances:
            a = sin^2(delta_phi/2) + cos(phi1) * cos(phi2) * sin^2(delta_lambda/2)
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            d = R * c

    Decision Points:
        Selected over Vincenty or Karney ellipsoidal geodesics to eliminate external C
        libraries (e.g., GeographicLib/GDAL). The maximum spherical error is under 0.5%,
        which is well within tolerance for municipal address proximity searches.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    sin_half_phi = math.sin(delta_phi / 2.0)
    sin_half_lambda = math.sin(delta_lambda / 2.0)

    a = (
        sin_half_phi * sin_half_phi
        + math.cos(phi1) * math.cos(phi2) * sin_half_lambda * sin_half_lambda
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))

    return EARTH_RADIUS_KM * c


def calculate_bounding_box(
    latitude: float, longitude: float, radius_km: float
) -> BoundingBox:
    """Derive minimum and maximum coordinate boundaries enclosing a search radius.

    Algorithm & Mathematical Considerations:
        1. Latitude delta is approximately constant: delta_lat = (radius / R) * (180 / pi).
        2. Longitude delta scales with latitude due to meridian convergence:
           delta_lon = (radius / (R * cos(lat))) * (180 / pi).
           To avoid clipping the circular search radius, delta_lon is calculated using
           the latitude closest to the poles within the box (max_abs_lat), where
           longitudinal spacing is narrowest.

    Edge Cases Handled:
        - Non-positive radius: Returns an empty envelope collapsed to the origin point.
        - Polar caps: When min_lat <= -90 or max_lat >= 90, the search disk touches a pole,
          meaning all longitudes [-180.0, 180.0] must be included.
        - Antimeridian crossing: When the longitude bounds extend beyond -180 or +180 degrees,
          coordinates wrap around the 180th meridian. The is_antimeridian_wrapped flag is set
          so the database query applies a disjunctive (lon >= min OR lon <= max) filter.
    """
    if radius_km <= 0.0:
        return BoundingBox(
            min_lat=latitude,
            max_lat=latitude,
            min_lon=longitude,
            max_lon=longitude,
            is_antimeridian_wrapped=False,
        )

    delta_lat = math.degrees(radius_km / EARTH_RADIUS_KM)
    min_lat = max(-90.0, latitude - delta_lat)
    max_lat = min(90.0, latitude + delta_lat)

    if min_lat <= -90.0 or max_lat >= 90.0:
        return BoundingBox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=-180.0,
            max_lon=180.0,
            is_antimeridian_wrapped=False,
        )

    max_abs_lat = max(abs(min_lat), abs(max_lat))
    cos_lat = math.cos(math.radians(max_abs_lat))

    if cos_lat < 1e-9:
        return BoundingBox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=-180.0,
            max_lon=180.0,
            is_antimeridian_wrapped=False,
        )

    delta_lon = math.degrees(radius_km / (EARTH_RADIUS_KM * cos_lat))

    if delta_lon >= 180.0:
        return BoundingBox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=-180.0,
            max_lon=180.0,
            is_antimeridian_wrapped=False,
        )

    raw_min_lon = longitude - delta_lon
    raw_max_lon = longitude + delta_lon

    if raw_min_lon < -180.0:
        normalized_min_lon = raw_min_lon + 360.0
        return BoundingBox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=normalized_min_lon,
            max_lon=raw_max_lon,
            is_antimeridian_wrapped=True,
        )
    elif raw_max_lon > 180.0:
        normalized_max_lon = raw_max_lon - 360.0
        return BoundingBox(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=raw_min_lon,
            max_lon=normalized_max_lon,
            is_antimeridian_wrapped=True,
        )

    return BoundingBox(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=raw_min_lon,
        max_lon=raw_max_lon,
        is_antimeridian_wrapped=False,
    )
