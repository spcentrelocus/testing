import asyncio
import httpx
import json
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.building import Building
from app.models.user import User
from app.core.security import create_access_token

async def targeted_verify():
    async with AsyncSessionLocal() as session:
        # Get Science Tower by name if possible, or just the first one
        # Based on seed script, assuming first one is Science Tower
        result = await session.execute(select(Building))
        building = result.scalars().first()
        
        if not building:
            print("No building found.")
            return

        user_result = await session.execute(select(User).where(User.id == building.user_id))
        user = user_result.scalars().first()
        
        token = create_access_token(subject=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"Testing Baseline for {building.name}...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/baseline/calculate",
                json={"building_id": str(building.id), "method": "historical_12_months"},
                headers=headers,
                timeout=30.0
            )
            
            data = response.json()
            print("API Response:", json.dumps(data, indent=2))

        # Verify DB Storage
        print("\nChecking Database History...")
        history_result = await session.execute(
            select(BaselineHistory)
            .where(BaselineHistory.building_id == building.id)
            .order_by(desc(BaselineHistory.created_at))
        )
        history = history_result.scalars().first()
        if history:
            print(f"Found History Record: Period={history.period}, Raw={history.raw_kwh}, Adjusted={history.adjusted_kwh}")
        else:
            print("No history record found!")

from sqlalchemy import desc
from app.models.baseline import BaselineHistory

if __name__ == "__main__":
    asyncio.run(targeted_verify())
