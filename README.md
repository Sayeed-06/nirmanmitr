# NirmanMitr - Production SaaS App

NirmanMitr is a commercial B2B SaaS web application designed for contractors, civil engineers, quantity surveyors, and engineering students to instantly understand every BOQ (Bill of Quantities) item.

## Features

- **BOQ Parsing Engine**: Automatically parses uploaded BOQ files (PDF, Excel, CSV).
- **DSR Knowledge Base**: Pre-populated with CPWD Delhi Schedule of Rates (DSR) items, their execution steps, common mistakes, and required materials.
- **Smart Matching**: Deterministically matches BOQ items to DSR knowledge using Regex and keyword heuristics, completely avoiding unpredictable AI inference.
- **Clean UI/UX**: Premium, high-quality dashboard built with Next.js, Radix UI, and Tailwind CSS.
- **Admin Dashboard**: Specialized views for manual review and data augmentation of the knowledge base.

## Architecture

This project is built using a Clean Architecture approach:

### Backend (Python/FastAPI)
- **Framework**: FastAPI (async, high-performance)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration**: Alembic
- **Parsers**:
  - `pdfplumber` / `camelot-py` (PDF)
  - `openpyxl` (Excel)
  - `pandas` (CSV)
- **Storage**: Pluggable storage backend (Local FileSystem or Supabase)

### Frontend (Next.js/React)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI Primitives
- **State Management**: React Query (TanStack Query)
- **Authentication**: Clerk (Placeholder integrations)

## Project Structure

```
nirmanmitr/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── core/           # Configuration & App setup
│   │   ├── db/             # SQLAlchemy sessions & Alembic
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── parser/         # Core parsing engine (PDF/Excel/CSV)
│   │   ├── repositories/   # Data access layer
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Business logic (Upload, Parse, Match)
│   │   └── storage/        # Storage provider abstractions
│   ├── scripts/            # Database seeders
│   └── alembic/            # Database migrations
│
└── frontend/
    ├── src/
    │   ├── app/            # Next.js App Router pages
    │   ├── components/     # Reusable React components (Knowledge Card, UI)
    │   ├── lib/            # Utilities & API client
    │   └── types/          # TypeScript interfaces
    └── public/             # Static assets
```

## Setup & Local Development

### 1. Database
Ensure you have a running PostgreSQL instance. Create a database named `nirmanmitr`.

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a .env file with your DATABASE_URL
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed initial DSR data
python scripts/seed_dsr.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install

# Start the Next.js development server
npm run dev
```

The frontend runs on `http://localhost:3000` and automatically proxies `/api` requests to the FastAPI backend running on port 8000.

## Future Phases (Placeholders)
The application architecture is explicitly designed to support the following upcoming features:
- **AI Chatbot**: Contextual AI for project-specific Q&A (UI placeholder included).
- **Video Integration**: Explainer videos for DSR items (UI placeholder included).

---
*Built with precision for civil engineering excellence.*
