
import asyncio
from datetime import datetime
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models.building import Building
from app.models.meter import MeterReading, DataSource

# Data for 2025
SCIENCE_TOWER_DATA = [
    {"month": 1, "kwh": 162000}, {"month": 2, "kwh": 162000}, {"month": 3, "kwh": 216000},
    {"month": 4, "kwh": 270000}, {"month": 5, "kwh": 324000}, {"month": 6, "kwh": 324000},
    {"month": 7, "kwh": 270000}, {"month": 8, "kwh": 243000}, {"month": 9, "kwh": 216000},
    {"month": 10, "kwh": 189000}, {"month": 11, "kwh": 162000}, {"month": 12, "kwh": 162000}
]

TECH_PARK_DATA = [
    {"month": 1, "kwh": 216000}, {"month": 2, "kwh": 216000}, {"month": 3, "kwh": 288000},
    {"month": 4, "kwh": 360000}, {"month": 5, "kwh": 432000}, {"month": 6, "kwh": 432000},
    {"month": 7, "kwh": 360000}, {"month": 8, "kwh": 324000}, {"month": 9, "kwh": 288000},
    {"month": 10, "kwh": 252000}, {"month": 11, "kwh": 216000}, {"month": 12, "kwh": 216000}
]

async def seed_meter_readings():
    async with AsyncSessionLocal() as session:
        # Fetch all buildings
        result = await session.execute(select(Building))
        buildings = result.scalars().all()

        if len(buildings) < 2:
            print("Error: Need at least 2 buildings to seed specific data.")
            return

        print(f"Found {len(buildings)} buildings. clearing old readings...")
        
        # Clear existing readings for these buildings
        building_ids = [b.id for b in buildings]
        await session.execute(delete(MeterReading).where(MeterReading.building_id.in_(building_ids)))
        
        # We will cycle through buildings if more than 2, but primarily target the first 2
        datasets = [SCIENCE_TOWER_DATA, TECH_PARK_DATA]
        dataset_names = ["Science Tower Data", "Tech Park Data"]

        new_readings = []
        
        # Sort buildings by created_at or id to ensure deterministic order if possible, 
        # though default sort usually matches insertion order.
        # We'll just use the list order.
        
        for idx, building in enumerate(buildings):
            if idx >= len(datasets):
                print(f"Skipping building {building.name} (no more datasets provided)")
                continue

            data = datasets[idx]
            data_name = dataset_names[idx]
            print(f"Seeding {data_name} for building: {building.name} (ID: {building.id})")

            for entry in data:
                # Create timestamp for 2025 (using 1st of each month at 12:00 PM)
                try:
                    reading_time = datetime(2025, entry["month"], 1, 12, 0, 0)
                except ValueError:
                     # Handle potential issues with days if we picked something other than 1
                     continue

                reading = MeterReading(
                    time=reading_time,
                    building_id=building.id,
                    value_kwh=float(entry["kwh"]),
                    source=DataSource.MANUAL
                )
                new_readings.append(reading)

        session.add_all(new_readings)
        await session.commit()
        
        print(f"Successfully added {len(new_readings)} meter readings.")

if __name__ == "__main__":
    asyncio.run(seed_meter_readings())
