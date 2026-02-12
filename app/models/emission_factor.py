import uuid
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id: Mapped[str] = mapped_column(String, index=True) # e.g., "US-CA", "IN-MH"
    region_name: Mapped[str] = mapped_column(String)
    factor_kg_per_kwh: Mapped[float] = mapped_column(Float)
    year: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String) # e.g., "EPA", "CEA"
