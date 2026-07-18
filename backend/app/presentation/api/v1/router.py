from fastapi import APIRouter
from app.presentation.api.v1.endpoints import health, auth, venue, parking, assistant

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(venue.router)
api_router.include_router(parking.router)
api_router.include_router(assistant.router)
