"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.api.v1 import api_router
from app.utils.logging import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    # Startup
    logger.info(
        "Starting TechJays Lead AI",
        version=__version__,
        environment=settings.environment,
    )

    # Initialize services
    try:
        # Import here to avoid circular imports
        from app.core.database import engine
        from app.core.vector_db import get_vector_db

        # Test database connection
        logger.info("Connecting to database...")
        # Note: actual connection happens on first query

        # Initialize vector database
        logger.info("Initializing vector database...")
        vector_db = get_vector_db()
        logger.info(
            "Vector database ready",
            collection_count=vector_db.get_collection_count(),
        )

        logger.info("Application startup complete")
    except Exception as e:
        logger.error("Startup error", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="TechJays Lead AI",
    description="AI-powered lead discovery and outreach platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TechJays Lead AI",
        "version": __version__,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }


# Health endpoint at root level (for easier access)
@app.get("/health", tags=["Health"])
async def root_health():
    """Quick health check at root level."""
    return {"status": "ok", "version": __version__}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
