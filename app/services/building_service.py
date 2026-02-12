from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from pydantic import UUID4

from app.models.building import Building
from app.schemas.building import BuildingCreate, BuildingUpdate

async def get_building(db: AsyncSession, building_id: UUID4) -> Optional[Building]:
    result = await db.execute(select(Building).filter(Building.id == building_id))
    return result.scalars().first()

async def get_user_buildings(db: AsyncSession, user_id: UUID4, skip: int = 0, limit: int = 100) -> List[Building]:
    result = await db.execute(select(Building).filter(Building.user_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_building(db: AsyncSession, building: BuildingCreate, user_id: UUID4) -> Building:
    db_building = Building(
        user_id=user_id,
        **building.model_dump()
    )
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building

async def update_building(
    db: AsyncSession, db_building: Building, building_update: BuildingUpdate
) -> Building:
    update_data = building_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_building, key, value)
    
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building

async def delete_building(db: AsyncSession, building_id: UUID4) -> Optional[Building]:
    result = await db.execute(select(Building).filter(Building.id == building_id))
    db_building = result.scalars().first()
    if db_building:
        await db.delete(db_building)
        await db.commit()
    return db_building
