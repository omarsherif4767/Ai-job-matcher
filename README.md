# Antigravity AI Project

AI-powered career intelligence platform with a single LangGraph agent.

## Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL (running locally or via Docker)
- Qdrant (running locally or via Docker)
- OpenRouter API Key

## Quick Start

### 1. Configure Environment
```bash
# Copy and fill in your API key
cp backend/.env.example backend/.env
# Edit backend/.env and set your OPENROUTER_API_KEY
```

### 2. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
playwright install chromium
```

### 3. Start Services (Docker - recommended)
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=antigravity_db postgres:15
docker run -d -p 6333:6333 qdrant/qdrant
```

### 4. Start the Backend
```bash
python run.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 5. Start the Frontend
```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:3000
```

## Tech Stack

| Layer | Technology |
|---|---|
| AI Agent | LangGraph (single stateful agent) |
| LLM Provider | OpenRouter API |
| Chat / Parsing | Qwen3 30B / Qwen3 30B Instruct |
| Matching / Cover Letters | DeepSeek V3 |
| Embeddings | BAAI/bge-small-en-v1.5 (fastembed/ONNX) |
| Scraping | Playwright (headless Chromium) |
| Backend | FastAPI + SQLAlchemy + asyncpg |
| Relational DB | PostgreSQL |
| Vector DB | Qdrant |
| Frontend | Next.js + Tailwind CSS |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/resume/upload` | Upload and parse a resume (PDF/DOCX) |
| POST | `/api/jobs/scrape` | Trigger Playwright scraper |
| POST | `/api/jobs/match` | Score candidate vs job (DeepSeek V3) |
| POST | `/api/cover-letter/generate` | Generate application materials |
| POST | `/api/chat` | Talk to AI career assistant |

## Project Structure

```
backend/
├── main.py              # FastAPI server entry point
├── config.py            # Settings & OpenRouter configuration
├── api/routes.py        # REST API endpoints
├── graph/agent.py       # Single LangGraph Agent workflow
├── graph/state.py       # Agent state schema
├── tools/parser.py      # Resume parser (Qwen3 30B)
├── tools/matcher.py     # Job matcher (DeepSeek V3)
├── tools/cover_letter.py# Cover letter generator (DeepSeek V3)
├── tools/phase2_tools.py# Phase 2: Interview coach, skill-gap
├── database/models.py   # PostgreSQL ORM models
├── database/session.py  # Async SQLAlchemy session
├── database/qdrant_client.py # Qdrant vector store
└── embeddings/bge_embeddings.py # BGE embeddings (fastembed)

scrapers/
├── base_scraper.py               # Playwright base class
├── greenhouse.py                 # Greenhouse ATS scraper
├── lever.py                      # Lever ATS scraper
├── workable_ashby_remoteok.py   # Workable, Ashby, RemoteOK scrapers
└── normalizer.py                 # Job data normalization schema

frontend/
└── app/page.js          # Interactive Next.js dashboard
```
