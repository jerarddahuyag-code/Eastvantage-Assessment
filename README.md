# Eastvantage Address Book API

Minimal, production-ready address book API built with FastAPI, SQLite, and the CQRS pattern.
It supports full address validation, coordinate persistence, and spatial proximity search.

---

## Features

- **FastAPI with async SQLite**: Powered by SQLAlchemy 2.0 and `aiosqlite` for non-blocking asynchronous database operations.
- **CQRS architecture**: Clean separation between state-mutating commands (create, update, delete) and read-only query projections.
- **Geospatial proximity search**: Efficient proximity filtering combining indexed SQL bounding box queries with in-memory Haversine distance calculations and sorting.
- **Strict validation**: Coordinates constrained to valid geographic ranges (-90 to 90 latitude, -180 to 180 longitude) with trimmed string field sanitization via Pydantic v2.
- **Automatic migrations**: Managed through Alembic with automatic migration execution during application startup.
- **Structured logging**: Dedicated HTTP middleware tracking request IDs, client IP addresses, route paths, response status codes, and execution duration in milliseconds.

---

## Requirements

- Python 3.14 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip` / `venv`

---

## Setup and execution

### Option 1: Using `uv` (Recommended)

Clone the repository and enter the directory:

```bash
cd "Eastvantage Assessment"
```

Install dependencies and start the server:

```bash
uv run uvicorn app.main:app --reload
```

The database schema and tables are automatically migrated on startup.
You can open the interactive API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Option 2: Using standard `venv` and `pip`

```bash
cd "Eastvantage Assessment"
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload
```

---

## Running automated tests

Run the complete test suite with `pytest`:

```bash
uv run pytest
```

The test suite covers:
- Haversine mathematical calculations and boundary handling.
- Address validation rules (latitude, longitude, empty fields).
- Address lifecycle operations (create, read by ID, paginated listing, full update, partial update, delete).
- Proximity search distance filtering, radius exclusion, and ascending distance sorting.

---

## Project structure

```
Eastvantage Assessment/
├── alembic/                      # Database migration scripts
│   ├── env.py
│   └── versions/                 # Versioned migration revisions
├── alembic.ini                   # Alembic configuration
├── app/
│   ├── api/                      # Routing and dependency injection
│   │   ├── deps.py               # CQRS handler dependency providers
│   │   └── v1/
│   │       ├── api.py            # API v1 aggregator
│   │       └── endpoints/
│   │           └── addresses.py  # Address REST endpoints
│   ├── core/                     # Application settings, logging, and exceptions
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── db/                       # Database engine, session, and migrations
│   │   ├── base.py
│   │   ├── migrations.py
│   │   └── session.py
│   ├── domain/                   # CQRS Commands, Queries, and Geo service
│   │   ├── commands/
│   │   │   ├── create_address.py
│   │   │   ├── delete_address.py
│   │   │   └── update_address.py
│   │   ├── queries/
│   │   │   ├── get_address.py
│   │   │   ├── get_nearby_addresses.py
│   │   │   └── list_addresses.py
│   │   └── services/
│   │       └── geo.py            # Haversine distance and bounding box calculations
│   ├── models/                   # SQLAlchemy declarative models
│   │   └── address.py
│   ├── schemas/                  # Pydantic validation schemas
│   │   └── address.py
│   └── main.py                   # FastAPI application factory and lifespan
├── tests/                        # Pytest suite with isolated test database
│   ├── conftest.py
│   ├── test_api.py
│   └── test_geo.py
├── pyproject.toml                # Project metadata and dependencies
└── README.md
```

---

## API specification

### 1. Create address

- **Endpoint**: `POST /api/v1/addresses`
- **Status code**: `201 Created`

```bash
curl -X POST "http://localhost:8000/api/v1/addresses" \
  -H "Content-Type: application/json" \
  -d '{
    "street": "100 Ayala Avenue",
    "city": "Makati",
    "state_province": "Metro Manila",
    "postal_code": "1226",
    "country": "Philippines",
    "latitude": 14.5547,
    "longitude": 121.0244
  }'
```

### 2. List addresses (paginated)

- **Endpoint**: `GET /api/v1/addresses?offset=0&limit=20`
- **Status code**: `200 OK`

```bash
curl -X GET "http://localhost:8000/api/v1/addresses?offset=0&limit=10"
```

### 3. Get address by identifier

- **Endpoint**: `GET /api/v1/addresses/{address_id}`
- **Status code**: `200 OK`

```bash
curl -X GET "http://localhost:8000/api/v1/addresses/<address-uuid>"
```

### 4. Full update address (PUT)

- **Endpoint**: `PUT /api/v1/addresses/{address_id}`
- **Status code**: `200 OK`

```bash
curl -X PUT "http://localhost:8000/api/v1/addresses/<address-uuid>" \
  -H "Content-Type: application/json" \
  -d '{
    "street": "200 Buendia Avenue",
    "city": "Makati",
    "state_province": "Metro Manila",
    "postal_code": "1200",
    "country": "Philippines",
    "latitude": 14.5600,
    "longitude": 121.0150
  }'
```

### 5. Partial update address (PATCH)

- **Endpoint**: `PATCH /api/v1/addresses/{address_id}`
- **Status code**: `200 OK`

```bash
curl -X PATCH "http://localhost:8000/api/v1/addresses/<address-uuid>" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Taguig",
    "postal_code": "1634"
  }'
```

### 6. Delete address

- **Endpoint**: `DELETE /api/v1/addresses/{address_id}`
- **Status code**: `204 No Content`

```bash
curl -X DELETE "http://localhost:8000/api/v1/addresses/<address-uuid>"
```

### 7. Search addresses within distance

- **Endpoint**: `GET /api/v1/addresses/nearby?latitude={lat}&longitude={lon}&radius_km={radius}&limit={limit}`
- **Status code**: `200 OK`

Returns matching addresses within the given radius (in kilometers), annotated with their calculated distance and sorted from nearest to farthest.

```bash
curl -X GET "http://localhost:8000/api/v1/addresses/nearby?latitude=14.5547&longitude=121.0244&radius_km=5.0"
```

Response payload format:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "street": "BGC High Street",
    "city": "Taguig",
    "state_province": "Metro Manila",
    "postal_code": "1634",
    "country": "Philippines",
    "latitude": 14.5510,
    "longitude": 121.0350,
    "created_at": "2026-10-21T09:20:00Z",
    "updated_at": "2026-10-21T09:20:00Z",
    "distance_km": 1.225
  }
]
```
