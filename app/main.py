from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="""
    Carbonexia AI Carbon Credit MRV Platform API.
    
    ## Features
    * **Buildings**: Manage building data.
    * **Meters**: Ingest energy data (JSON/CSV).
    * **MRV**: Calculate baselines, savings, and carbon credits.
    * **Emission Factors**: Manage regional carbon intensity.
    """,
    version="1.0.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Carbonexia API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "db": "unknown", "redis": "unknown"}
