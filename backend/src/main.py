"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Policy Warehouse API for healthcare policy document management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Policy Warehouse API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


# Import and include routers
from .api.routes import ingestion, policies
app.include_router(ingestion.router, prefix="/v1/ingestion", tags=["ingestion"])
app.include_router(policies.router, prefix="/v1/policies", tags=["policies"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
