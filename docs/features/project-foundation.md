# Feature: Project Foundation

**Slug:** project-foundation
**Status:** In Progress
**Owner:** TechJays Engineering
**Created:** 2026-01-30
**Last updated:** 2026-01-30

## 1. Objective

- **Problem:** No project structure exists for the TechJays Lead AI platform
- **Solution:** Set up the foundational backend infrastructure with Python FastAPI, PostgreSQL, ChromaDB, and core project structure
- **Success Criteria:**
  - FastAPI server running with health check endpoint
  - PostgreSQL database connected with initial schema
  - ChromaDB vector store initialized
  - Groq LLM integration working
  - Docker Compose for local development
  - Environment configuration system

## 2. Scope

### In scope

- Python FastAPI backend setup
- PostgreSQL database with initial Lead/Company models
- ChromaDB vector database setup
- Groq LLM client integration
- Project directory structure
- Docker Compose configuration
- Environment variable management
- Basic health check and status endpoints
- Logging and error handling setup
- Requirements/dependencies management

### Out of scope

- Frontend/UI (separate feature)
- Web scraping implementation (separate feature)
- Chatbot conversation logic (separate feature)
- Email sending functionality
- CRM integrations
- Production deployment (Render setup)

## 3. User Stories

- As a developer, I want a well-structured Python project so that I can easily add new features
- As a developer, I want Docker Compose so that I can run all services locally with one command
- As a developer, I want database models defined so that I can store lead data
- As a developer, I want Groq LLM integrated so that I can build AI features

## 4. Requirements

### Functional Requirements

- FR1: FastAPI application with automatic OpenAPI docs at `/docs`
- FR2: PostgreSQL connection with SQLAlchemy ORM
- FR3: ChromaDB client for vector embeddings
- FR4: Groq client for LLM inference
- FR5: Health check endpoint at `/health`
- FR6: API versioning with `/api/v1/` prefix
- FR7: CORS middleware configured
- FR8: Environment-based configuration (dev/staging/prod)

### Non-functional Requirements

- **Performance:** API response < 200ms for health check
- **Security:** No secrets in code, all via environment variables
- **Reliability:** Graceful shutdown, connection pooling
- **Observability:** Structured JSON logging, request tracing

## 5. UX / API Contract

### API Endpoints (Foundation)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (DB, Vector DB status) |
| GET | `/api/v1/status` | System status and version |
| GET | `/docs` | OpenAPI documentation |

### Example Response

```json
// GET /health
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "database": "connected",
    "vector_db": "connected",
    "llm": "available"
  },
  "timestamp": "2026-01-30T12:00:00Z"
}
```

## 6. Data Model Impact

### New Tables

**leads**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_name | VARCHAR(255) | Company name |
| company_domain | VARCHAR(255) | Company website domain |
| industry | VARCHAR(100) | Industry category |
| employee_count | INTEGER | Number of employees |
| funding_stage | VARCHAR(50) | Seed, Series A, etc. |
| location | VARCHAR(255) | HQ location |
| ai_adoption_score | FLOAT | 0-100 AI adoption score |
| lead_score | FLOAT | 0-100 overall lead score |
| status | VARCHAR(50) | new, contacted, qualified, etc. |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**contacts**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| email | VARCHAR(255) | Email address |
| email_confidence | FLOAT | 0-100 confidence score |
| job_title | VARCHAR(255) | Job title |
| linkedin_url | VARCHAR(500) | LinkedIn profile URL |
| created_at | TIMESTAMP | Record creation time |

**data_sources**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| source_type | VARCHAR(50) | linkedin, apollo, hunter, etc. |
| source_url | VARCHAR(500) | Original data URL |
| raw_data | JSONB | Raw scraped/API data |
| fetched_at | TIMESTAMP | When data was fetched |

### Migrations

- Use Alembic for database migrations
- Initial migration creates all tables

## 7. Integration Impact

### External Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| PostgreSQL | Primary database | `DATABASE_URL` env var |
| ChromaDB | Vector embeddings | Local persistent storage |
| Groq | LLM inference | `GROQ_API_KEY` env var |

### Environment Variables

```
DATABASE_URL=postgresql://user:pass@localhost:5432/leadgen
GROQ_API_KEY=gsk_xxx
GROQ_MODEL=llama-3.3-70b-versatile
CHROMADB_PATH=./data/chromadb
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 8. Code Impact

### New files/modules

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings and environment
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py    # API router
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py      # PostgreSQL connection
│   │   ├── vector_db.py     # ChromaDB client
│   │   └── llm.py           # Groq client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── lead.py          # Lead SQLAlchemy model
│   │   ├── contact.py       # Contact model
│   │   └── data_source.py   # DataSource model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── lead.py          # Pydantic schemas
│   │   └── health.py        # Health response schema
│   └── utils/
│       ├── __init__.py
│       └── logging.py       # Logging configuration
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_health.py
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── pyproject.toml
```

## 9. Test Plan

### Unit Tests

- `test_config.py` - Configuration loading
- `test_database.py` - Database connection
- `test_health.py` - Health endpoint responses

### Integration Tests

- `test_api_health.py` - Full health check with real DB
- `test_llm_connection.py` - Groq API connectivity

### E2E Tests

- Docker Compose up → Health check passes → Shutdown

### Regression Risks

- None (greenfield project)

## 10. Rollout Plan

- **Feature flag:** No (foundation required for all features)
- **Migration strategy:** Fresh database, no existing data
- **Backward compatibility:** N/A (new project)
- **Deployment notes:**
  1. Run `docker-compose up -d` for local dev
  2. Access API at http://localhost:8000
  3. Access docs at http://localhost:8000/docs

## 11. Checklist

- [x] Plan reviewed
- [x] Tests added/updated
- [ ] Lint/test/build pass
- [ ] Docs updated
- [ ] PR raised
- [ ] PR approved
