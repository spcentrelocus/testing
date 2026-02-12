from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4

from app.api import deps
from app.schemas.emission_factor import EmissionFactor, EmissionFactorCreate, EmissionFactorUpdate
from app.models.user import User
from app.services import emission_factor_service

router = APIRouter()

@router.get("/", response_model=List[EmissionFactor])
async def read_emission_factors(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve emission factors. Public endpoint (read-only usually, but let's keep it simple).
    """
    return await emission_factor_service.get_all_emission_factors(db, skip=skip, limit=limit)

@router.post("/", response_model=EmissionFactor)
async def create_emission_factor(
    *,
    db: AsyncSession = Depends(deps.get_db),
    factor_in: EmissionFactorCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new emission factor. Admin only? For now allow any auth user.
    """
    # Check uniqueness
    existing = await emission_factor_service.get_emission_factor_by_region_year(
        db, region_id=factor_in.region_id, year=factor_in.year
    )
    if existing:
        raise HTTPException(status_code=400, detail="Emission factor for this region and year already exists")
    
    return await emission_factor_service.create_emission_factor(db, factor_in=factor_in)

@router.get("/{factor_id}", response_model=EmissionFactor)
async def read_emission_factor(
    *,
    db: AsyncSession = Depends(deps.get_db),
    factor_id: UUID4,
) -> Any:
    """
    Get emission factor by ID.
    """
    factor = await emission_factor_service.get_emission_factor(db, factor_id=factor_id)
    if not factor:
        raise HTTPException(status_code=404, detail="Emission factor not found")
    return factor
