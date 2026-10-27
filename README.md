# EventHorizon AI — AI-Powered Global Tech Event Discovery Platform

> **EventHorizon AI** is a production-oriented discovery and verification engine for hackathons, technical conferences, engineering competitions, and developer workshops. It features strict **India-first geographic resolution**, evidence-based multi-factor verification, and a zero-hallucination grounded AI assistant.

---

## 1. Key Capabilities & Architectural Pillars

1. **India-First Geographic Integrity**:
   - Explicit canonical model covering all **28 Indian states** and **8 union territories** (ISO 3166-2:IN).
   - Zero cross-state leakage: events in Karnataka or Delhi will never silently leak into Telangana listings.
   - Strict separation of organizer headquarters from physical venue locations.
   - Online events are isolated in virtual collections and never force-assigned to physical state queues.
2. **Evidence-Based Verification**:
   - Immutable `EventSourceObservation` evidence store preserving raw source circulars and canonical URLs.
   - Multi-factor verification engine checking URL domain reputation, chronological date consistency, and venue proof.
   - Dedicated unverified queues for community inspection and administrative review.
3. **Automated Discovery Engine & Security**:
   - Multi-adapter architecture (Devpost, Unstop, Meetup, RSS/Atom feeds, GDG Community events).
   - Built-in SSRF protection blocking RFC 1918, loopback, and cloud metadata subnets (`169.254.169.254`).
   - Deterministic metadata extraction (Schema.org JSON-LD Event schema, OpenGraph).
4. **Server-Side Free Browsing Allowance**:
   - Anonymous visitors receive 5 free full event detail inspections.
   - Server-enforced via client IP/session tracking to prevent abuse while allowing frictionless initial discovery.
5. **Ground-Truth AI Assistant**:
   - Queries real database records; guaranteed zero hallucinated dates, prizes, or registration links.
   - Directly embeds verified event citations with links to official organizer portals.
6. **Audited Administrative Operations**:
   - Role-Based Access Control (`user`, `moderator`, `admin`, `super_admin`).
   - Real calculated metrics (no fake charts or mock statistics).
   - High-risk bulk deletion requires `super_admin` privilege and typing the exact confirmation phrase `DELETE ALL EVENTS PERMANENTLY`.

---

## 2. Technology Stack

- **Frontend**: React 19, Vite, Tailwind CSS, Lucide React, Axios, React Markdown.
- **Backend**: Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic.
- **Database**: PostgreSQL (Production) / SQLite Async with aiosqlite (Zero-friction local dev & tests).
- **Security & Auth**: Bcrypt, JWT (HS256), SSRF IP-range validation.
- **Testing**: Pytest, Pytest-Asyncio, HTTPX ASGI Client.
- **Deployment**: Docker, Docker Compose, Nginx.

---

## 3. Quickstart Guide (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### Backend Setup
```bash
# 1. Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Run backend server
.\.venv\Scripts\python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Frontend Setup
```bash
# 1. Navigate to frontend
cd frontend

# 2. Start Vite development server
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 4. Running the Automated Test Suite

EventHorizon AI includes comprehensive test coverage for geographic leakage, SSRF blocking, verification heuristics, and authentication:

```bash
# Run full pytest suite with verbose output
.\.venv\Scripts\python -m pytest -v
```

### Verified Test Cases
- `backend/tests/test_geo_leakage.py`: Proves all 28 states + 8 UTs are loaded and physical events never leak across state borders.
- `backend/tests/test_ssrf_fetcher.py`: Verifies loopback (`127.0.0.1`) and AWS metadata IP (`169.254.169.254`) requests are blocked.
- `backend/tests/test_verification.py`: Confirms URL canonicalization, title token overlap, and invalid date rejection.
- `backend/tests/test_auth.py`: Tests user registration, password hashing, and the anonymous 5-view browsing limit.
- `backend/tests/test_health.py`: Verifies database ping latency and operational status.

---

## 5. Docker Deployment

Deploy the entire stack with Docker Compose:

```bash
docker-compose up --build
```

Services started:
- `backend` on `http://localhost:8000`
- `frontend` (Nginx) on `http://localhost:5173`
- `db` (PostgreSQL 16) on `localhost:5432`
- `redis` (Redis 7) on `localhost:6379`

---

## 6. Seed Credentials

Initial SuperAdmin account automatically provisioned on first launch:
- **Email**: `admin@eventhorizon.ai`
- **Password**: `Admin@EventHorizon2026!`
