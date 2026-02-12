from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import UUID4

from app.models.emission_factor import EmissionFactor
from app.schemas.emission_factor import EmissionFactorCreate, EmissionFactorUpdate

async def get_emission_factor(db: AsyncSession, factor_id: UUID4) -> Optional[EmissionFactor]:
    result = await db.execute(select(EmissionFactor).filter(EmissionFactor.id == factor_id))
    return result.scalars().first()

async def get_emission_factor_by_region_year(db: AsyncSession, region_id: str, year: int) -> Optional[EmissionFactor]:
    result = await db.execute(select(EmissionFactor).filter(
        EmissionFactor.region_id == region_id,
        EmissionFactor.year == year
    ))
    return result.scalars().first()

async def get_all_emission_factors(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[EmissionFactor]:
    result = await db.execute(select(EmissionFactor).offset(skip).limit(limit))
    return result.scalars().all()

async def create_emission_factor(db: AsyncSession, factor_in: EmissionFactorCreate) -> EmissionFactor:
    db_factor = EmissionFactor(**factor_in.model_dump())
    db.add(db_factor)
    await db.commit()
    await db.refresh(db_factor)
    return db_factor

async def update_emission_factor(
    db: AsyncSession, db_factor: EmissionFactor, factor_update: EmissionFactorUpdate
) -> EmissionFactor:
    update_data = factor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_factor, key, value)
    
    db.add(db_factor)
    await db.commit()
    await db.refresh(db_factor)
    return db_factor
