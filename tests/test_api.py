import pytest
from httpx import AsyncClient

BASE_URL = "/api/v1/addresses"

SAMPLE_ADDRESS_PAYLOAD = {
    "street": "100 Ayala Avenue",
    "city": "Makati",
    "state_province": "Metro Manila",
    "postal_code": "1226",
    "country": "Philippines",
    "latitude": 14.5547,
    "longitude": 121.0244,
}


@pytest.mark.asyncio
async def test_create_address_success(client: AsyncClient) -> None:
    response = await client.post(BASE_URL, json=SAMPLE_ADDRESS_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["street"] == SAMPLE_ADDRESS_PAYLOAD["street"]
    assert data["latitude"] == SAMPLE_ADDRESS_PAYLOAD["latitude"]
    assert data["longitude"] == SAMPLE_ADDRESS_PAYLOAD["longitude"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_address_validation_errors(client: AsyncClient) -> None:
    invalid_lat = {**SAMPLE_ADDRESS_PAYLOAD, "latitude": 95.0}
    res_lat = await client.post(BASE_URL, json=invalid_lat)
    assert res_lat.status_code == 422

    invalid_lon = {**SAMPLE_ADDRESS_PAYLOAD, "longitude": -190.0}
    res_lon = await client.post(BASE_URL, json=invalid_lon)
    assert res_lon.status_code == 422

    blank_street = {**SAMPLE_ADDRESS_PAYLOAD, "street": "   "}
    res_street = await client.post(BASE_URL, json=blank_street)
    assert res_street.status_code == 422


@pytest.mark.asyncio
async def test_get_address_by_id(client: AsyncClient) -> None:
    create_res = await client.post(BASE_URL, json=SAMPLE_ADDRESS_PAYLOAD)
    address_id = create_res.json()["id"]

    get_res = await client.get(f"{BASE_URL}/{address_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == address_id


@pytest.mark.asyncio
async def test_get_address_not_found(client: AsyncClient) -> None:
    res = await client.get(f"{BASE_URL}/non-existent-uuid")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == "ADDRESS_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_addresses_paginated(client: AsyncClient) -> None:
    for i in range(3):
        payload = {
            **SAMPLE_ADDRESS_PAYLOAD,
            "street": f"Street {i}",
        }
        await client.post(BASE_URL, json=payload)

    res = await client.get(f"{BASE_URL}?offset=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_full_update_address_put(client: AsyncClient) -> None:
    create_res = await client.post(BASE_URL, json=SAMPLE_ADDRESS_PAYLOAD)
    address_id = create_res.json()["id"]

    updated_payload = {
        "street": "200 Buendia Avenue",
        "city": "Makati",
        "state_province": "Metro Manila",
        "postal_code": "1200",
        "country": "Philippines",
        "latitude": 14.5600,
        "longitude": 121.0150,
    }
    put_res = await client.put(f"{BASE_URL}/{address_id}", json=updated_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["street"] == "200 Buendia Avenue"
    assert data["latitude"] == 14.5600


@pytest.mark.asyncio
async def test_partial_update_address_patch(client: AsyncClient) -> None:
    create_res = await client.post(BASE_URL, json=SAMPLE_ADDRESS_PAYLOAD)
    address_id = create_res.json()["id"]

    patch_payload = {"city": "Taguig", "postal_code": "1634"}
    patch_res = await client.patch(f"{BASE_URL}/{address_id}", json=patch_payload)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["city"] == "Taguig"
    assert data["postal_code"] == "1634"
    assert data["street"] == SAMPLE_ADDRESS_PAYLOAD["street"]


@pytest.mark.asyncio
async def test_delete_address(client: AsyncClient) -> None:
    create_res = await client.post(BASE_URL, json=SAMPLE_ADDRESS_PAYLOAD)
    address_id = create_res.json()["id"]

    del_res = await client.delete(f"{BASE_URL}/{address_id}")
    assert del_res.status_code == 204

    get_res = await client.get(f"{BASE_URL}/{address_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_nearby_proximity_search(client: AsyncClient) -> None:
    origin_lat = 14.5547
    origin_lon = 121.0244

    # Point 1: ~1.2 km away
    point_1 = {
        **SAMPLE_ADDRESS_PAYLOAD,
        "street": "BGC Entrance",
        "latitude": 14.5510,
        "longitude": 121.0350,
    }
    # Point 2: ~3.8 km away
    point_2 = {
        **SAMPLE_ADDRESS_PAYLOAD,
        "street": "Mandaluyong Center",
        "latitude": 14.5790,
        "longitude": 121.0360,
    }
    # Point 3: ~14.0 km away
    point_3 = {
        **SAMPLE_ADDRESS_PAYLOAD,
        "street": "Quezon City Circle",
        "latitude": 14.6500,
        "longitude": 121.0500,
    }

    await client.post(BASE_URL, json=point_1)
    await client.post(BASE_URL, json=point_2)
    await client.post(BASE_URL, json=point_3)

    # Search with 5 km radius: should match point_1 and point_2, exclude point_3
    res = await client.get(
        f"{BASE_URL}/nearby?latitude={origin_lat}&longitude={origin_lon}&radius_km=5.0"
    )
    assert res.status_code == 200
    results = res.json()
    assert len(results) == 2

    assert results[0]["street"] == "BGC Entrance"
    assert results[1]["street"] == "Mandaluyong Center"
    assert results[0]["distance_km"] < results[1]["distance_km"]
    assert results[0]["distance_km"] <= 5.0
    assert results[1]["distance_km"] <= 5.0
