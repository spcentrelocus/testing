import asyncio
import httpx
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.building import Building
from app.models.user import User
from app.core.security import create_access_token

async def verify_baseline():
    async with AsyncSessionLocal() as session:
        # Get a building
        result = await session.execute(select(Building))
        building = result.scalars().first()
        if not building:
            print("No building found.")
            return

        # Get a user (or just create a token for a fake user if validation is loose, 
        # but better to use real one)
        # Actually proper way is to login, but we can just mint a token if we have secret.
        # However, `get_current_user` checks DB. So let's get the owner of the building.
        user_result = await session.execute(select(User).where(User.id == building.user_id))
        user = user_result.scalars().first()
        if not user:
            # Fallback to any user
            user_result = await session.execute(select(User))
            user = user_result.scalars().first()

        token = create_access_token(subject=user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Calculate
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/baseline/calculate",
                json={"building_id": str(building.id), "method": "historical_12_months"},
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(verify_baseline())
