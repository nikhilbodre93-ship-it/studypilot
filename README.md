# StudyPilot ✈️
### AI-Powered Adaptive Revision Coach for Students

StudyPilot is an intelligent, full-stack adaptive learning assistant designed to optimize student recall and syllabus coverage before exams. It features Bayesian Knowledge Tracing (BKT), SuperMemo SM-2 spaced repetition, grounded retrieval-augmented generation (RAG) using PyMuPDF, prompt-injection defense, and multi-provider LLM support.

---

## Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                              STUDYPILOT FRONTEND                                  |
|            React 18 + Vite + TypeScript + Tailwind CSS + TanStack Query           |
|                                                                                   |
|  [01 Dashboard]       [02 My Learning]      [03 Revision Planner] [04 Roadmap]    |
|  [05 Study Notes]     [06 Quizzes]          [07 Flashcards]       [08 AI Tutor]   |
|  [09 Focus Timer]     [10 Progress Analytics]                                     |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST + SSE Streaming
                                           v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                      Python 3.11 + SQLAlchemy 2.0 + Pydantic v2                   |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |  Cognitive Engines |  |    RAG & Ingestion    |  |     LLM Provider Layer    |  |
|  |  - BKT Mastery     |  |  - PyMuPDF Extraction|  |  - Anthropic Claude       |  |
|  |  - SM-2 Intervals  |  |  - ~800 Token Chunks |  |  - OpenAI-compatible      |  |
|  |  - Priority Queue  |  |  - Page Citations    |  |  - Ollama (Local)         |  |
|  |  - Pomodoro Packing|  |  - Injection Defense |  |  - Deterministic Mock     |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | SQLAlchemy ORM
                                           v
+-----------------------------------------------------------------------------------+
|                                DATA PERSISTENCE                                   |
|      SQLite (Local Dev: studypilot.db)  /  PostgreSQL 16 (Production Docker)      |
+-----------------------------------------------------------------------------------+
```

---

## Key Features

1. **Explainable Revision Scheduler (Phase 2)**:
   - **Bayesian Knowledge Tracing (BKT)**: Dynamically computes $P(L_t)$ from practice accuracy while keeping empirical accuracy distinct.
   - **SuperMemo SM-2**: Computes ease factors, repetitions, and due dates for flashcard recall.
   - **Multi-Factor Priority Scoring**: Weights mastery deficit, recent error rate, overdue cards, difficulty, and exam proximity.

2. **RAG & Document Ingestion (Phase 4)**:
   - Native support for PDF, TXT, and Markdown uploads.
   - Chunking into ~800-token blocks with 100-token overlap and page-level citations.
   - Strictly data-bounded prompts protecting against prompt injection.

3. **Multi-Model AI Generation (Phase 4)**:
   - Structured JSON validation with automatic Pydantic schema repair and exponential backoff retry.
   - Server-Sent Events (SSE) streaming for real-time Socratic tutoring.
   - In-memory generation caching and per-user daily quota enforcement.

4. **Calm Editorial UI (Phase 3 & 5)**:
   - Designed with an organic palette (`#F4F6F1` background, `#2F5D46` forest green).
   - High-contrast, accessible typography with responsive drawers and focus indicators.

---

## Switching the LLM Provider

StudyPilot abstracts the AI layer through a pluggable `BaseLLMProvider` interface. You can switch providers instantly by editing your `.env` file or environment variables:

### 1. Deterministic Mock (Default / Offline Dev & Testing)
```env
LLM_PROVIDER=mock
```
*Zero API keys or internet connection required. Returns valid structured JSON and streaming tokens.*

### 2. Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 3. OpenAI or OpenAI-Compatible (Groq, OpenRouter, Together, vLLM)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### 4. Local Ollama
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

# Run migrations & seed data
alembic upgrade head
python -m app.seed

# Start backend server
uvicorn app.main:app --reload --port 8000
```
Backend API interactive documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
### 3. Demo Credentials
The seeded local database includes a ready-to-test student account:
- **Email:** `demo@studypilot.io`
- **Password:** `StudyPilot2026!`

---

## 🌐 Free Cloud Deployment (Neon + Render + Vercel)

See **[DEPLOY.md](file:///c:/Users/nikhi/studypilot/DEPLOY.md)** for a step-by-step click-by-click guide to deploy StudyPilot permanently for free:
- **Database:** [Neon](https://neon.tech) (Serverless PostgreSQL)
- **Backend:** [Render](https://render.com) (Docker Web Service) or [Koyeb](https://koyeb.com)
- **Frontend:** [Vercel](https://vercel.com) (Vite React SPA)
- **Keep-Alive:** [UptimeRobot](https://uptimerobot.com) (Free 5-minute ping)

---

## Running with Docker Compose

To deploy the entire production stack (PostgreSQL 16, Redis 7, FastAPI backend, and Nginx frontend):

```bash
docker compose up --build
```

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Postgres Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## Running Tests

### Backend Test Suite (Pytest)
```bash
cd backend
pytest -v
```
*Executes all 46 tests covering authentication, BKT mastery, SM-2 calculations, scheduling algorithms, mock LLM generation, RAG ingestion, and tutor streaming.*

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
*Executes all 17 tests covering UI component states, countdown timers, navigation, and page render workflows.*

---

## Security & Verification

- **Zero Client-Side Secrets**: All LLM API keys and database credentials reside exclusively in the backend runtime.
- **Strict User Ownership Isolation**: Every query and mutation is filtered against the authenticated user ID.
- **Prompt Injection Defense**: Uploaded materials are enclosed in `<STUDY_MATERIAL_CONTEXT>` blocks and treated strictly as passive data.
- **Upload Sanitization**: File uploads are restricted by MIME type and size (max 25MB).
