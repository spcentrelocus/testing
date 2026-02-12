import asyncio
import pandas as pd
import uuid
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services import meter_service
from app.schemas.meter import MeterReadingCreate, DataSource

async def process_csv_async(file_path: str, building_id: str):
    try:
        # 1. Read CSV
        df = pd.read_csv(file_path)
        
        # 2. Normalize columns (Simple assumption: timestamp, value)
        # Expected Headers: timestamp, kwh
        if 'timestamp' not in df.columns or 'kwh' not in df.columns:
            print(f"Invalid CSV format in {file_path}")
            return
            
        readings = []
        for _, row in df.iterrows():
            readings.append(MeterReadingCreate(
                time=pd.to_datetime(row['timestamp']),
                building_id=uuid.UUID(building_id),
                value_kwh=float(row['kwh']),
                source=DataSource.CSV,
                meta_data={"filename": file_path}
            ))

        # 3. Insert Batch
        async with AsyncSessionLocal() as db:
            count = await meter_service.create_meter_readings_batch(db, readings)
            print(f"Successfully inserted {count} readings from {file_path}")

    except Exception as e:
        print(f"Error processing CSV {file_path}: {e}")

@celery_app.task(name="process_meter_csv")
def process_meter_csv(file_path: str, building_id: str):
    """
    Wrapper to run async ingestion in Celery.
    """
    asyncio.run(process_csv_async(file_path, building_id))
