from fastapi import APIRouter
from app.api import auth
from app.api.endpoints import buildings, emission_factors, meters, mrv, baseline

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
api_router.include_router(emission_factors.router, prefix="/emission-factors", tags=["emission-factors"])
api_router.include_router(meters.router, prefix="/meters", tags=["meters"])
api_router.include_router(mrv.router, prefix="/mrv", tags=["mrv"])
api_router.include_router(baseline.router, prefix="/baseline", tags=["baseline"])

