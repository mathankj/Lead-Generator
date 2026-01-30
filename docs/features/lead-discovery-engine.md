# Feature: Lead Discovery Engine

**Slug:** lead-discovery-engine
**Status:** In Progress
**Owner:** TechJays Engineering
**Created:** 2026-01-30
**Last updated:** 2026-01-30

## 1. Objective

- **Problem:** No automated way to discover and collect AI company leads
- **Solution:** Build a multi-source lead discovery engine with API integrations, web scraping, enrichment pipeline, and scoring algorithm
- **Success Criteria:**
  - Apollo.io API integration working (50 leads/month free tier)
  - Hunter.io API integration for email discovery
  - Lead CRUD API endpoints functional
  - Lead scoring algorithm implemented
  - Data enrichment pipeline running
  - 50+ leads discoverable per day

## 2. Scope

### In scope

- Apollo.io API integration (company/contact search)
- Hunter.io API integration (email finder/verifier)
- Lead CRUD endpoints (create, read, update, delete, list)
- Contact CRUD endpoints
- Lead scoring algorithm (ML-based weights)
- Data enrichment service
- Background task processing (Celery)
- Rate limiting for external APIs
- Search and filtering API

### Out of scope

- LinkedIn scraping (high risk, defer to Phase 2)
- Crunchbase scraping (defer to Phase 2)
- Automated outreach/email sending
- Chatbot interface (separate feature)
- Frontend UI (separate feature)

## 3. User Stories

- As a BA, I want to search for AI companies by criteria so that I can find potential leads
- As a BA, I want to see lead scores so that I can prioritize outreach
- As a BA, I want contact emails verified so that I don't waste time on invalid addresses
- As a developer, I want API endpoints so that I can build a frontend

## 4. Requirements

### Functional Requirements

- FR1: Apollo.io search integration (company search, people search)
- FR2: Hunter.io email finder and verifier integration
- FR3: Lead CRUD API with pagination and filtering
- FR4: Contact CRUD API linked to leads
- FR5: Lead scoring based on AI adoption, company size, funding
- FR6: Bulk import from CSV/JSON
- FR7: Export leads to CSV/JSON
- FR8: Background job processing for enrichment
- FR9: Rate limiting to respect API quotas

### Non-functional Requirements

- **Performance:** Search response < 500ms, enrichment < 5s per lead
- **Security:** API keys stored securely, rate limiting per user
- **Reliability:** Retry failed API calls, graceful degradation
- **Observability:** Log all API calls, track enrichment success rate

## 5. UX / API Contract

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/leads` | List leads with pagination/filters |
| POST | `/api/v1/leads` | Create a new lead |
| GET | `/api/v1/leads/{id}` | Get lead details |
| PUT | `/api/v1/leads/{id}` | Update lead |
| DELETE | `/api/v1/leads/{id}` | Delete lead |
| POST | `/api/v1/leads/search` | Search leads by criteria |
| POST | `/api/v1/leads/{id}/enrich` | Enrich lead with external data |
| POST | `/api/v1/leads/{id}/score` | Calculate lead score |
| POST | `/api/v1/leads/import` | Bulk import leads |
| GET | `/api/v1/leads/export` | Export leads to CSV |
| GET | `/api/v1/contacts` | List contacts |
| POST | `/api/v1/contacts` | Create contact |
| GET | `/api/v1/contacts/{id}` | Get contact |
| PUT | `/api/v1/contacts/{id}` | Update contact |
| DELETE | `/api/v1/contacts/{id}` | Delete contact |
| POST | `/api/v1/contacts/{id}/verify-email` | Verify email address |
| POST | `/api/v1/discovery/search` | Search external sources |
| GET | `/api/v1/discovery/sources` | List available data sources |

### Example Requests/Responses

```json
// POST /api/v1/discovery/search
{
  "query": "AI companies in San Francisco",
  "filters": {
    "location": "San Francisco, CA",
    "industry": ["AI", "Machine Learning"],
    "employee_count_min": 50,
    "employee_count_max": 500,
    "funding_stage": ["Series A", "Series B"]
  },
  "sources": ["apollo"],
  "limit": 20
}

// Response
{
  "results": [
    {
      "company_name": "Anthropic",
      "domain": "anthropic.com",
      "industry": "Artificial Intelligence",
      "employee_count": 150,
      "location": "San Francisco, CA",
      "funding_stage": "Series C",
      "ai_adoption_score": 95,
      "source": "apollo"
    }
  ],
  "total": 47,
  "sources_queried": ["apollo"],
  "quota_remaining": {"apollo": 45}
}
```

```json
// POST /api/v1/leads/{id}/enrich
// Response
{
  "lead_id": "uuid",
  "enrichment_results": {
    "apollo": {"status": "success", "data": {...}},
    "hunter": {"status": "success", "emails_found": 3}
  },
  "new_score": 78.5,
  "contacts_added": 2
}
```

## 6. Data Model Impact

### New Tables

**api_credentials**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| service | VARCHAR(50) | apollo, hunter, etc. |
| api_key | VARCHAR(500) | Encrypted API key |
| quota_limit | INTEGER | Monthly quota |
| quota_used | INTEGER | Current usage |
| quota_reset_at | TIMESTAMP | When quota resets |
| created_at | TIMESTAMP | Record creation |

**enrichment_jobs**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | FK to leads |
| status | VARCHAR(20) | pending, running, completed, failed |
| sources | JSONB | Sources to query |
| results | JSONB | Enrichment results |
| started_at | TIMESTAMP | Job start time |
| completed_at | TIMESTAMP | Job completion time |
| error | TEXT | Error message if failed |

### Modified Tables

**leads** - Add columns:
- `enriched_at` TIMESTAMP
- `enrichment_status` VARCHAR(20)

**contacts** - Add columns:
- `email_verified_at` TIMESTAMP
- `email_source` VARCHAR(50)

## 7. Integration Impact

### External Services

| Service | Purpose | Auth | Rate Limit |
|---------|---------|------|------------|
| Apollo.io | Company/contact search | API Key | 60 req/hr |
| Hunter.io | Email finder/verifier | API Key | 50 req/mo (free) |

### Environment Variables

```
APOLLO_API_KEY=your_apollo_key
HUNTER_API_KEY=your_hunter_key
CELERY_BROKER_URL=redis://localhost:6379/0
```

## 8. Code Impact

### New files/modules

```
backend/app/
├── api/v1/endpoints/
│   ├── leads.py           # Lead CRUD endpoints
│   ├── contacts.py        # Contact CRUD endpoints
│   └── discovery.py       # Discovery/search endpoints
├── services/
│   ├── __init__.py
│   ├── apollo.py          # Apollo.io client
│   ├── hunter.py          # Hunter.io client
│   ├── enrichment.py      # Enrichment pipeline
│   ├── scoring.py         # Lead scoring algorithm
│   └── discovery.py       # Discovery orchestration
├── tasks/
│   ├── __init__.py
│   ├── celery_app.py      # Celery configuration
│   └── enrichment.py      # Background enrichment tasks
├── schemas/
│   ├── discovery.py       # Discovery request/response schemas
│   └── contact.py         # Contact schemas
└── models/
    ├── api_credential.py  # API credentials model
    └── enrichment_job.py  # Enrichment job model
```

### Modified files

- `backend/app/api/v1/router.py` - Add new routers
- `backend/app/models/__init__.py` - Export new models
- `backend/requirements.txt` - Add celery, httpx

## 9. Test Plan

### Unit Tests (Added)

- `backend/tests/test_apollo_client.py` - Mock Apollo API responses ✓
- `backend/tests/test_hunter_client.py` - Mock Hunter API responses ✓
- `backend/tests/test_scoring.py` - Scoring algorithm edge cases ✓
- `backend/tests/test_leads_crud.py` - Lead CRUD operations ✓
- `backend/tests/test_contacts_crud.py` - Contact CRUD operations ✓

### Integration Tests (Added)

- `backend/tests/test_discovery_api.py` - Full discovery flow ✓

### Deferred Tests

- `test_enrichment_pipeline.py` - Enrichment with mocked APIs (Phase 2)
- `test_export_import.py` - CSV/JSON import/export (Phase 2)

### E2E Tests

- Create lead → Enrich → Score → Export

### Regression Risks

- Database schema changes (migration required)
- New dependencies may conflict

## 10. Rollout Plan

- **Feature flag:** No (core feature)
- **Migration strategy:** Alembic migration for new tables
- **Backward compatibility:** Additive changes only
- **Deployment notes:**
  1. Run database migrations
  2. Set API keys in environment
  3. Start Celery worker for background tasks
  4. Test with Apollo free tier first

## 11. Checklist

- [x] Plan reviewed
- [x] Tests added/updated
- [ ] Lint/test/build pass
- [x] Docs updated
- [x] PR raised (https://github.com/mathankj/Lead-Generator/pull/2)
- [ ] PR approved
