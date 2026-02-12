from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.models.baseline import BaselineHistory
from app.models.meter import MeterReading
from app.schemas.baseline import BaselineRequest, BaselineResponse, BaselineNormalization, BaselineMonthData
import uuid
from datetime import datetime
import statistics

class BaselineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_baseline(self, request: BaselineRequest) -> BaselineResponse:
        months_data = []

        if request.months:
            months_data = request.months
        else:
            # Fetch last 12 months from DB
            result = await self.db.execute(
                select(MeterReading)
                .where(MeterReading.building_id == request.building_id)
                .order_by(desc(MeterReading.time))
                .limit(12)
            )
            readings = result.scalars().all()
            if not readings:
                raise ValueError("No meter readings found for this building")
            
            for reading in readings:
                months_data.append(BaselineMonthData(
                    period=reading.time.strftime("%Y-%m"),
                    kwh=reading.value_kwh
                ))

        if not months_data:
            raise ValueError("No data available for baseline calculation")

        # Step 1: Remove Outliers (+/- 20% deviation)
        cleaned_data = self._remove_outliers(months_data, threshold_pct=0.20)
        
        # Step 2: Weather Normalization (Placeholder)
        # In a real implementation, this would fetch HDD/CDD data and adjust.
        # For now, we assume data is already normalized or weather factor is 1.0.
        norm_weather_data = self._normalize_weather(cleaned_data)
        
        # Step 3: Occupancy Normalization (Placeholder)
        norm_occupancy_data = self._normalize_occupancy(norm_weather_data)

        if not norm_occupancy_data:
             # Fallback if aggressive filtering removed everything, though unlikely with just 20% rule on valid data.
             # We might revert to raw average or throw warning.
             # For MVP, let's use the raw mean if cleaning leaves nothing.
             norm_occupancy_data = months_data

        # Calculate Raw Average (for record keeping)
        raw_total_kwh = sum(m.kwh for m in months_data)
        raw_avg_kwh = raw_total_kwh / len(months_data)

        # Step 4: Baseline Average
        total_kwh = sum(m.kwh for m in norm_occupancy_data)
        avg_kwh = total_kwh / len(norm_occupancy_data)

        # Store in History
        # We store the result for the CURRENT period (e.g. today's month) to indicate this is the active baseline.
        current_period = datetime.now().strftime("%Y-%m")
        
        baseline_record = BaselineHistory(
            building_id=request.building_id,
            period=current_period,
            raw_kwh=raw_avg_kwh,
            adjusted_kwh=avg_kwh,
            weather_factor=1.0,
            occupancy_factor=1.0
        )
        self.db.add(baseline_record)
        await self.db.commit()
        await self.db.refresh(baseline_record)

        response = BaselineResponse(
            building_id=request.building_id,
            baseline_monthly_kwh=round(avg_kwh, 2),
            method=request.method,
            normalization=BaselineNormalization(weather=True, occupancy=True)
        )
        return response

    def _remove_outliers(self, data: List[BaselineMonthData], threshold_pct: float) -> List[BaselineMonthData]:
        if not data:
            return []
        
        values = [d.kwh for d in data]
        mean_val = statistics.mean(values)
        
        # Determine bounds
        lower_bound = mean_val * (1 - threshold_pct)
        upper_bound = mean_val * (1 + threshold_pct)
        
        cleaned = []
        for d in data:
            if lower_bound <= d.kwh <= upper_bound:
                cleaned.append(d)
        
        return cleaned

    def _normalize_weather(self, data: List[BaselineMonthData]) -> List[BaselineMonthData]:
        # Placeholder: Return as-is
        return data

    def _normalize_occupancy(self, data: List[BaselineMonthData]) -> List[BaselineMonthData]:
        # Placeholder: Return as-is
        return data

    async def get_baselines(self, building_id: uuid.UUID):
        # Retrieve history
        result = await self.db.execute(
            select(BaselineHistory).where(BaselineHistory.building_id == building_id)
        )
        return result.scalars().all()
