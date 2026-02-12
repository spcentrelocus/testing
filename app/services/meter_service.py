from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from app.models.meter import MeterReading
from app.schemas.meter import MeterReadingCreate

async def create_meter_readings_batch(db: AsyncSession, readings: List[MeterReadingCreate]) -> int:
    """
    Bulk insert meter readings.
    """
    db_readings = [
        MeterReading(**reading.model_dump())
        for reading in readings
    ]
    db.add_all(db_readings)
    await db.commit()
    return len(db_readings)

async def get_meter_readings(
    db: AsyncSession, building_id: str, limit: int = 1000
) -> List[MeterReading]:
    result = await db.execute(
        select(MeterReading)
        .filter(MeterReading.building_id == building_id)
        .order_by(MeterReading.time.desc())
        .limit(limit)
    )
    return result.scalars().all()
