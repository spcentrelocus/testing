# Carbonexia – AI Carbon Credit MRV Platform

> **Comprehensive Markdown Documentation (AWS-Free Architecture)**
>
> This document is the technical specification for the **Carbonexia** platform, adapted for a **Cloud-Agnostic / Local-First** architecture.
>
> **Stack Changes:**
> - AWS Cognito → **FastAPI + JWT**
> - Amazon Timestream → **TimescaleDB (PostgreSQL)**
> - AWS Lambda → **Celery + Redis**
> - ECS Fargate → **Docker / Docker Compose**

---

## 1. Platform Overview

Carbonexia is a **SaaS platform** that automates **Measurement, Reporting, and Verification (MRV)** of building energy savings and converts them into **eligible carbon credits** using AI-assisted workflows.

**Standards supported**:
- ISO 14064
- Verra (VM0018 / VM0038)
- Gold Standard (Energy Efficiency)
- India Carbon Market (ICM)

---

## 2. High-Level Architecture

### Core Layers
1. **Data Ingestion Layer**: API endpoints for CSV/JSON meter data.
2. **Processing & MRV Engine Layer**: Python services (FastAPI + Celery) for baseline calculation and anomaly detection.
3. **AI Services Layer**: Python-based OCR and Normalization logic.
4. **Storage Layer**: Unified SQL + Time-Series database (TimescaleDB).
5. **API Layer**: FastAPI (Python).
6. **Frontend**: (Next.js - *Out of Scope for this backend task*).

### Event-Driven Architecture (Added)
* Async processing using **Celery + Redis** (replaces AWS SQS + Lambda)
* Events handled:
  * OCR completion
  * Baseline computed
  * MRV calculation finished
  * Report generated

---

## 3. Technology Stack (AWS-Free)

| Component | Architecture |
|---------|------------|
| **API Server** | FastAPI (Python) running in Docker |
| **Async Tasks** | Celery (with Redis Broker) |
| **OCR / AI** | Python Libraries (Tesseract/PaddleOCR) or External API |
| **Database** | TimescaleDB (PostgreSQL Extension) |
| **File Storage** | Local Volume / MinIO (S3 Compatible) |
| **Auth** | JWT (OAuth2PasswordBearer) |
| **Messaging** | Redis (as Message Broker) |
| **Caching** | Redis |
| **Logs** | Standard Output (Docker Logs) / ELK Stack (Optional) |
| **Networking** | Docker Network |
| **CI/CD** | GitHub Actions |
| **Infra** | Docker Compose |

---

## 4. Deployment Blueprint (Docker Compose)

### Core Services
- **backend**: FastAPI application.
- **db**: TimescaleDB (PostgreSQL 14+).
- **redis**: Message broker and cache.
- **worker**: Celery worker for background jobs (OCR, Reporting).

### Docker Compose Example

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/carbonexia
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: timescale/timescaledb:latest-pg14
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=carbonexia
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  worker:
    build: .
    command: celery -A app.worker worker --loglevel=info
    depends_on:
      - redis
      - db

volumes:
  db_data:
```

---

## 5. Database Schema (TimescaleDB / PostgreSQL)

**Note:** TimescaleDB allows us to keep all tables in one database. `METER_READINGS` will be a **Hypertable**.

### RELATIONAL TABLES

#### users
- id (UUID, PK)
- email (VARCHAR, Unique)
- password_hash (VARCHAR)
- role (VARCHAR)
- created_at (TIMESTAMP)
- is_active (BOOLEAN)

#### buildings
- id (UUID, PK)
- user_id (FK -> users.id)
- name (VARCHAR)
- address (VARCHAR)
- building_type (VARCHAR)
- area_sqft (FLOAT)
- timezone (VARCHAR)
- occupancy_profile (JSONB)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### baseline_history
- id (UUID, PK)
- building_id (FK -> buildings.id)
- period_start (TIMESTAMP)
- period_end (TIMESTAMP)
- raw_kwh (FLOAT)
- adjusted_kwh (FLOAT)
- weather_factor (FLOAT)
- occupancy_factor (FLOAT)
- created_at (TIMESTAMP)

#### carbon_credits
- id (UUID, PK)
- building_id (FK -> buildings.id)
- period_start (TIMESTAMP)
- period_end (TIMESTAMP)
- co2_saved_tons (FLOAT)
- credits_issued (FLOAT)
- status (ENUM: PENDING, ISSUED, RETIRED)
- created_at (TIMESTAMP)

#### reports
- id (UUID, PK)
- building_id (FK -> buildings.id)
- generated_at (TIMESTAMP)
- file_path (VARCHAR)
- status (ENUM: PROCESSING, COMPLETED, FAILED)

### TIME-SERIES HYPERTABLES

#### meter_readings
*Converted to Hypertable partitioned by `timestamp`*
- time (TIMESTAMP, PK Component)
- building_id (UUID, FK -> buildings.id, PK Component)
- value_kwh (FLOAT)
- source (ENUM: API, CSV, MANUAL)

#### emission_factors
- region_id (VARCHAR)
- year (INTEGER)
- factor_kg_per_kwh (FLOAT)
- valid_from (TIMESTAMP)
- valid_to (TIMESTAMP)

---

## 6. Developer API Specifications

### Authentication
- **Standard JWT**
- Login Endpoint: `/auth/login` (Returns `access_token`)
- Header: `Authorization: Bearer <access_token>`

### Error Codes
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 422 Validation Error
- 500 Server Error

---

## 7. API Modules

### Auth
- POST /auth/register
- POST /auth/login
- POST /auth/refresh

### Building Management
- POST /buildings
- GET /buildings/{id}
- PATCH /buildings/{id}
- DELETE /buildings/{id}

### Baseline
- POST /baseline/calculate
- GET /baseline/{building_id}

### Meter Ingestion
- POST /meter/readings (Batch JSON)
- POST /meter/upload-csv (File Upload)
- GET /meter/{building_id}/readings

### MRV Engine
- GET /mrv/{building_id}/summary
- GET /mrv/{building_id}/savings

### Credits
- GET /credits/{building_id}
- POST /credits/issue

### Reports
231. POST /reports/generate
232. GET /reports/{report_id}/download

### Webhooks (Added)

**OCR Completion Webhook**
```json
{
  "event_type": "ocr_completed",
  "upload_id": "upl_xxx",
  "building_id": "uuid",
  "extracted": {
    "kwh": 42300,
    "billing_days": 30,
    "meter_number": "MTR-001"
  }
}
```

**Report Completion Webhook**
```json
{
  "event_type": "report_ready",
  "report_id": "rep_xxx",
  "file_path": "/reports/mrv_jan_2026.pdf"
}
```

### API REQUEST & RESPONSE CONTRACTS (Added)

#### Authentication

**POST /auth/login**
Request:
```json
{
  "email": "user@example.com",
  "password": "********"
}
```
Response:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

#### Building Management

**POST /buildings**
Request:
```json
{
  "name": "Tech Park Tower",
  "address": "DLF Phase II, Gurgaon",
  "building_type": "commercial_office",
  "area_sqft": 200000,
  "occupancy_profile": {
    "weekday": 85,
    "weekend": 20
  },
  "timezone": "Asia/Kolkata"
}
```
Response:
```json
{
  "building_id": "uuid",
  "status": "created"
}
```

#### Baseline Calculation

**POST /baseline/calculate**
Request:
```json
{
  "building_id": "uuid",
  "months": [
    { "period": "2024-01", "kwh": 38000 },
    { "period": "2024-02", "kwh": 41000 }
  ]
}
```
Response:
```json
{
  "baseline_monthly_kwh": 39500,
  "normalization": {
    "weather": true,
    "occupancy": true
  }
}
```

#### Meter Ingestion

**POST /meter/readings**
Request:
```json
{
  "building_id": "uuid",
  "timestamp": "2026-01-07T10:30:00Z",
  "kwh": 125.3
}
```
Response:
```json
{ "status": "accepted" }
```

#### MRV Summary

**GET /mrv/{building_id}/summary**
Response:
```json
{
  "baseline_monthly_kwh": 40433,
  "current_month_kwh": 35620,
  "savings_kwh": 4813,
  "co2_saved_kg": 3947,
  "eligible": true
}
```

#### Report Generation

**POST /reports/generate**
Request:
```json
{
  "building_id": "uuid",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31"
}
```
Response:
```json
{
  "report_id": "rep_xxx",
  "status": "processing"
}
```

---

## 8. Implementation Phases

### Phase 1: Foundation
- Project scaffolding (FastAPI, Docker)
- Database Setup (TimescaleDB)
- Authentication System (JWT)

### Phase 2: Ingestion & Baseline
- Meter Reading Hypertable
- CSV Upload Parsing (Pandas/Celery)
- Baseline Calculation Logic

### Phase 3: MRV Core
- Emission Factor Logic
- Savings Calculation (`Baseline - Actual`)
- API Endpoints for MRV data

### Phase 4: Reporting & AI
- PDF Generation (ReportLab/WeasyPrint)
- Celery Integration for long-running reports

### Sprint-Wise Execution Plan (Added)
* Sprint 1: Auth, DB, Docker
* Sprint 2: Baseline + OCR
* Sprint 3: Meter ingestion
* Sprint 4: MRV + eligibility
* Sprint 5: Credits
* Sprint 6: Reporting
* Sprint 7: Dashboard + QA


---

## 9. Non-Functional Requirements

### Security
- Password Hashing (bcrypt)
- Environment Variables for Secrets
- Docker Container isolation

### Performance
- TimescaleDB chunks for fast time-series queries.
- Redis caching for frequent aggregations.
- Async workers for heavy computations.

### Scalability & Performance (Added)
* Horizontal worker scaling
* TimescaleDB hypertables for meter data
* Redis caching for MRV aggregates

### Security & Compliance (Added)
* ISO 14064 compliant MRV flows
* Verra / Gold Standard aligned logic
* JWT-based role enforcement
* Audit logs stored in PostgreSQL


---

## 10. Carbon Methodology Formula

```
CO₂ Saved = (Baseline kWh – Actual kWh) × Emission Factor
1 Credit = 1 ton CO₂e
```

### Data Quality Rules
- **Missing Data**:
    - ≤ 5%: Linear Interpolation
    - 5% - 20%: Flag for review / Advanced Interpolation
    - > 20%: Reject period

### Carbon Methodology Rules Engine (Added)

#### Baseline Methods
* Historical (12 months)
* Weather normalized
* Occupancy normalized
* Regression based
* Static baseline

#### Additionality Rules
* Retrofit → eligible
* Occupancy drop / shutdown → ineligible
* Equipment failure → ineligible

#### Monitoring Rules
* Missing ≤ 5% → interpolate
* Missing 5–20% → flag
* Missing > 20% → reject

#### Eligibility
* Valid baseline
* Positive reduction
* Monitoring quality OK / INTERPOLATED


---

## 11. Future Roadmap (Added)
* IoT smart meter integrations
* Carbon marketplace APIs
* Blockchain audit trail (optional)

## ✅ End of Document
