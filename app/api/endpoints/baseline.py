from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.baseline import BaselineRequest, BaselineResponse
from app.services.baseline_service import BaselineService
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.post("/calculate", response_model=BaselineResponse)
async def calculate_baseline(
    request: BaselineRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = BaselineService(db)
    try:
        return await service.calculate_baseline(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{building_id}")
async def get_building_baselines(
    building_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = BaselineService(db)
    return await service.get_baselines(building_id)
