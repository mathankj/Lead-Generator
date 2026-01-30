# TechJays Lead AI - Quick Start Guide

## 1. Setup Environment

### Create `.env` file
```bash
cd backend
cp .env.example .env
```

### Get API Keys

**Apollo.io (50 credits/month free):**
1. Sign up at https://www.apollo.io/
2. Go to Settings → Integrations → API
3. Generate API key
4. Add to `.env`: `APOLLO_API_KEY=your_key`

**Hunter.io (25 searches/month free):**
1. Sign up at https://hunter.io/
2. Go to API section or https://hunter.io/api-keys
3. Copy your API key
4. Add to `.env`: `HUNTER_API_KEY=your_key`

**Groq (Free):**
1. Sign up at https://console.groq.com/
2. Generate API key
3. Add to `.env`: `GROQ_API_KEY=your_key`

## 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

## 3. Test API Keys

```bash
# Verify your API keys work
python test_api_keys.py
```

Expected output:
```
=== Testing Apollo.io API ===
✅ Apollo API working! Found 5 companies (total: 1234)

=== Testing Hunter.io API ===
✅ Hunter API working!
   Account: you@example.com
   Plan: Free
   Searches available: 25

🎉 All API keys are configured correctly!
```

## 4. Setup Database

### PostgreSQL
```bash
# Make sure PostgreSQL is running
# Update DATABASE_URL in .env with your credentials
DATABASE_URL=postgresql://user:password@localhost:5432/techjays_lead_ai
```

### Run Migrations (when available)
```bash
alembic upgrade head
```

## 5. Start the Server

```bash
uvicorn app.main:app --reload
```

Server starts at: http://localhost:8000

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 6. Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Search for Companies
```bash
curl -X POST "http://localhost:8000/api/v1/discovery/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI companies in San Francisco",
    "sources": ["apollo"],
    "limit": 5
  }'
```

### Create a Lead
```bash
curl -X POST "http://localhost:8000/api/v1/leads" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Anthropic",
    "company_domain": "anthropic.com",
    "industry": "Artificial Intelligence",
    "location": "San Francisco, CA"
  }'
```

## 7. Troubleshooting

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Check credentials are correct

### API Key Errors
- Run `python test_api_keys.py` to verify
- Check keys are in `.env` file
- Verify keys are valid on provider websites

### ChromaDB Error
```bash
pip install "numpy<2.0" chromadb==0.4.22
```

## 8. Next Steps

1. ✅ Configure API keys
2. ✅ Test connections
3. ✅ Start server
4. 📝 Create your first lead
5. 🔍 Test discovery search
6. 📊 Score and enrich leads
7. 📧 Find and verify contact emails

## Directory Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   │   ├── leads.py         # Lead CRUD
│   │   ├── contacts.py      # Contact CRUD
│   │   ├── discovery.py     # Discovery search
│   │   └── health.py        # Health checks
│   ├── services/            # External integrations
│   │   ├── apollo.py        # Apollo.io client
│   │   ├── hunter.py        # Hunter.io client
│   │   ├── scoring.py       # Lead scoring
│   │   └── enrichment.py    # Data enrichment
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # FastAPI app
├── tests/                   # Test files
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── test_api_keys.py        # API key verification
```

## Useful Commands

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_scoring.py -v

# Check code style
black app/
flake8 app/

# View logs
tail -f logs/app.log

# Database shell
psql $DATABASE_URL
```
