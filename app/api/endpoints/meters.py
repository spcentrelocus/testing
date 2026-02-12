from typing import List, Any
import shutil
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from app.tasks.ingestion import process_meter_csv

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4

from app.api import deps
from app.schemas.meter import MeterReadingCreate, MeterReadingResponse, MeterReading
from app.services import meter_service
from app.models.user import User

router = APIRouter()

@router.post("/batch", response_model=MeterReadingResponse, summary="Batch Ingest Readings", description="Ingest a list of meter readings (JSON format).")
async def ingest_meter_readings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    readings: List[MeterReadingCreate],
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Ingest a batch of meter readings.
    """
    # Validation: Ensure user owns the building(s)? 
    # For now assume API key/Token access grants ability to push.
    # Ideally checking every building_id in the list matches user access would be costly.
    
    count = await meter_service.create_meter_readings_batch(db, readings=readings)
    return {"status": "success", "count": count}

@router.post("/upload-csv", response_model=MeterReadingResponse, summary="Upload CSV", description="Upload a CSV file containing meter readings (`timestamp`, `kwh`). Processing happens in background.")
async def upload_csv(
    *,
    building_id: UUID4,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload CSV file for background processing.
    """
    # 1. Save file to disk
    os.makedirs("/tmp/uploads", exist_ok=True)
    file_location = f"/tmp/uploads/{uuid.uuid4()}.csv"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # 2. Trigger Celery Task
    # building_id must be passed as string to Celery (JSON serialization)
    process_meter_csv.delay(file_location, str(building_id))
    
    return {"status": "processing_started", "count": 0}

@router.get("/{building_id}", response_model=List[MeterReading])
async def get_readings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    limit: int = 1000,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get latest meter readings for a building.
    """
    readings = await meter_service.get_meter_readings(db, building_id=building_id, limit=limit)
    return readings
