from typing import Any, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from datetime import datetime

from app.api import deps
from app.services import mrv_service
from app.models.user import User

router = APIRouter()

@router.get("/{building_id}/summary", summary="MRV Summary", description="Calculate savings, CO2 reduction, and estimated credits for a given period.")
async def get_mrv_summary(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get MRV summary (Savings, CO2, Credits) for a period.
    """
    # Validation
    # check permission...

    return await mrv_service.calculate_savings(db, building_id, start_date, end_date)

@router.post("/{building_id}/baseline", summary="Set Baseline (Admin)", description="Manually set the baseline kWh for a specific period (YYYY-MM).")
async def set_baseline(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    period: str,
    raw_kwh: float,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Manually set baseline for a period (Admin/Manager function).
    """
    return await mrv_service.create_baseline(db, building_id, period, raw_kwh)
