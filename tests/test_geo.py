import math
import pytest
from app.domain.services.geo import (
    calculate_bounding_box,
    haversine_distance,
)


def test_haversine_distance_between_paris_and_london() -> None:
    # Paris (48.8566 N, 2.3522 E) to London (51.5074 N, 0.1278 W) is ~343.5 km
    distance = haversine_distance(48.8566, 2.3522, 51.5074, -0.1278)
    assert math.isclose(distance, 343.5, rel_tol=0.01)


def test_haversine_distance_same_point_is_zero() -> None:
    distance = haversine_distance(14.5995, 120.9842, 14.5995, 120.9842)
    assert distance == pytest.approx(0.0, abs=1e-6)


def test_calculate_bounding_box_clamps_latitude_at_poles() -> None:
    box = calculate_bounding_box(latitude=89.5, longitude=10.0, radius_km=100.0)
    assert box.max_lat == 90.0
    assert box.min_lon == -180.0
    assert box.max_lon == 180.0


def test_calculate_bounding_box_normal_radius() -> None:
    center_lat = 14.5995
    center_lon = 120.9842
    radius_km = 10.0

    box = calculate_bounding_box(
        latitude=center_lat, longitude=center_lon, radius_km=radius_km
    )

    assert box.min_lat < center_lat < box.max_lat
    assert box.min_lon < center_lon < box.max_lon
    assert not box.is_antimeridian_wrapped
