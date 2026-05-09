# ModelLogger: Research Memory OS for AI/ML Teams

ModelLogger is a persistent Research Memory OS designed to capture and structure research activity into a persistent memory graph.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL + pgvector, Redis, Pydantic v2
- **AI**: sentence-transformers (BAAI/bge-m3), LiteLLM
- **Infra**: Docker, Docker Compose

## Project Structure
```
app/
  api/          # API routes
  core/         # Configuration and utilities
  db/           # Database session and base classes
  models/       # SQLAlchemy models
  schemas/      # Pydantic schemas
  services/     # Business logic (e.g., embeddings)
  repositories/ # Data access layer
  workers/      # Background task handlers
  ingestion/    # Logic for raw data ingestion
  retrieval/    # Search and retrieval logic
  events/       # Event definitions and handling
  utils/        # Common utilities
```

## Example Training Workflows

We provide several example scripts to demonstrate ModelLogger's capabilities:

1. **Stable Training**: `python examples/stable_train.py`
2. **Failing (Divergence)**: `python examples/failing_train.py`
3. **BF16 Overflow**: `python examples/bf16_overflow.py`
4. **Tokenizer Regression**: `python examples/tokenizer_regression.py`

Run these scripts to populate the organizational memory and trigger live cognition alerts.

## Frontend Dashboard

A modern Next.js dashboard is provided for visualizing experiments and learnings.

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

### Dashboard Features
- **Live Cognition Feed**: Real-time WebSocket alerts and anomaly detection.
- **Failure Explorer**: Semantic search across historical failure patterns.
- **Experiment Timeline**: Chronological reconstruction of research activity.
- **Knowledge Graph**: Visualization of experiment relationships and learning evolution.
- **Automated Postmortems**: AI-generated reports for failed experiments.

## Getting Started

### 1. Environment Setup
```bash
cp .env.example .env
```

### 2. Run with Docker Compose
```bash
docker-compose up --build
```

### 3. Database Migrations
```bash
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
```

## Key Endpoints
- `POST /api/v1/memory/ingest`: Ingest a new research memory event.
- `POST /api/v1/memory/find_similar`: Find semantically similar historical events using pgvector.
- `POST /api/v1/experiments/`: Create a new experiment root.
