from fastapi import APIRouter
from .endpoints import endpoints_router

# Main API router
api_router = APIRouter()

# Register endpoint routes
api_router.include_router(endpoints_router)
