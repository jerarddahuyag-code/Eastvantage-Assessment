"""API v1 router registry."""

from fastapi import APIRouter
from app.api.v1.endpoints.addresses import router as addresses_router

api_v1_router = APIRouter()
api_v1_router.include_router(addresses_router)
