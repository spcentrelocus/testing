from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime
from pydantic import UUID4

from app.models.baseline import BaselineHistory
from app.models.meter import MeterReading
from app.models.building import Building
from app.services import emission_factor_service

async def get_baseline(db: AsyncSession, building_id: UUID4, period: str) -> Optional[BaselineHistory]:
    result = await db.execute(select(BaselineHistory).filter(
        BaselineHistory.building_id == building_id,
        BaselineHistory.period == period
    ))
    return result.scalars().first()

async def create_baseline(
    db: AsyncSession, building_id: UUID4, period: str, raw_kwh: float
) -> BaselineHistory:
    baseline = BaselineHistory(
        building_id=building_id,
        period=period,
        raw_kwh=raw_kwh,
        adjusted_kwh=raw_kwh # No adjustment for MVP
    )
    db.add(baseline)
    await db.commit()
    await db.refresh(baseline)
    return baseline

async def calculate_savings(
    db: AsyncSession, building_id: UUID4, period_start: datetime, period_end: datetime
) -> Dict[str, Any]:
    """
    Calculate savings for a specific time range.
    Formula: (Baseline - Actual) * EmissionFactor
    """
    # 1. Get Actual kWh from Meter Readings
    # Sum value_kwh where time is between start and end
    # Note: This simple sum assumes meter readings cover the whole period evenly.
    query = select(func.sum(MeterReading.value_kwh)).filter(
        MeterReading.building_id == building_id,
        MeterReading.time >= period_start,
        MeterReading.time <= period_end
    )
    result = await db.execute(query)
    actual_kwh = result.scalars().first() or 0.0

    # 2. Get Baseline Logic
    # For MVP, assume the "period" is the YYYY-MM of the start_date
    period_str = period_start.strftime("%Y-%m")
    baseline = await get_baseline(db, building_id, period_str)
    
    if not baseline:
        return {"error": f"No baseline found for period {period_str}"}
    
    baseline_kwh = baseline.adjusted_kwh

    # 3. Get Emission Factor
    # We need the region of the building first
    building_query = select(Building).filter(Building.id == building_id)
    building_res = await db.execute(building_query)
    building = building_res.scalars().first()
    
    if not building:
        return {"error": "Building not found"}
    
    # Simple logic: Extract region from address or lookup. 
    # For MVP, let's hardcode 'US-CA' or fetch from Building if we added region column (we didn't, using address/name).
    # Let's assume passed region or default.
    region_id = "US-CA" # Placeholder
    
    factor_obj = await emission_factor_service.get_emission_factor_by_region_year(
        db, region_id=region_id, year=period_start.year
    )
    
    factor_val = factor_obj.factor_kg_per_kwh if factor_obj else 0.5 # Default fallback
    
    # 4. Calculate
    savings_kwh = max(0, baseline_kwh - actual_kwh)
    co2_saved_kg = savings_kwh * factor_val
    credits_estimated = co2_saved_kg / 1000.0 # 1 Credit = 1 Ton

    return {
        "period": period_str,
        "baseline_kwh": baseline_kwh,
        "actual_kwh": actual_kwh,
        "savings_kwh": savings_kwh,
        "emission_factor": factor_val,
        "co2_saved_kg": co2_saved_kg,
        "credits_estimated": credits_estimated
    }
